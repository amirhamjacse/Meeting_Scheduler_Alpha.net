from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import filters, generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Meeting, MeetingNotification, Participant
from .serializers import (
    ConflictCheckSerializer,
    MeetingCreateSerializer,
    MeetingDetailSerializer,
    MeetingListSerializer,
    MeetingNotificationSerializer,
    ParticipantCreateSerializer,
    ParticipantSerializer,
    ParticipantStatusSerializer,
)
from .utils.conflict_detector import check_participants_conflicts
from .utils.ics_generator import (
    generate_ics_for_meeting,
    generate_ics_for_multiple_meetings,
)
from .utils.notifications import notify_all_participants


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def is_meeting_owner(user, meeting):
    """Return True if the given user created the meeting."""
    return meeting.created_by == user


def get_user_meetings(user):
    """
    Return all meetings the user owns or is a participant in.
    Results are pre-fetched with participants to avoid N+1 queries.
    """
    return (
        Meeting.objects.filter(created_by=user)
        | Meeting.objects.filter(participants__user=user)
    ).distinct().prefetch_related("participants")


# ===========================================================================
# Meeting views
# ===========================================================================

class MeetingListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/meetings/   List all meetings for the current user.
    POST /api/meetings/   Create a new meeting.

    Uses generics.ListCreateAPIView -- handles pagination, search,
    and ordering automatically via filter_backends.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "location"]
    ordering_fields = [
        "start_time", "end_time", "created_at", "title"
    ]
    ordering = ["start_time"]

    def get_queryset(self):
        qs = get_user_meetings(self.request.user)

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")
        if from_date:
            qs = qs.filter(start_time__date__gte=from_date)
        if to_date:
            qs = qs.filter(end_time__date__lte=to_date)

        return qs

    def get_serializer_class(self):
        # Use a lightweight serializer for the list view
        if self.request.method == "POST":
            return MeetingCreateSerializer
        return MeetingListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# ---------------------------------------------------------------------------

class MeetingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/meetings/{id}/   Retrieve full meeting details.
    PUT    /api/meetings/{id}/   Replace a meeting.
    PATCH  /api/meetings/{id}/   Partially update a meeting.
    DELETE /api/meetings/{id}/   Delete a meeting.

    Uses generics.RetrieveUpdateDestroyAPIView -- all four HTTP
    methods handled by the one class.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_user_meetings(self.request.user)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return MeetingCreateSerializer
        return MeetingDetailSerializer

    def perform_update(self, serializer):
        if not is_meeting_owner(self.request.user, self.get_object()):
            raise PermissionDenied(
                "Only the meeting organiser can edit it."
            )
        serializer.save()

    def perform_destroy(self, instance):
        if not is_meeting_owner(self.request.user, instance):
            raise PermissionDenied(
                "Only the meeting organiser can delete it."
            )
        instance.delete()


# ---------------------------------------------------------------------------

class MeetingCancelView(APIView):
    """
    POST /api/meetings/{id}/cancel/

    Manual APIView -- custom business logic (status guard + signal
    trigger) does not fit a generic view cleanly.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: MeetingDetailSerializer},
        description="Cancel a meeting and notify all participants.",
    )
    def post(self, request, pk):
        meeting = get_object_or_404(
            get_user_meetings(request.user), pk=pk
        )

        if not is_meeting_owner(request.user, meeting):
            return Response(
                {
                    "detail": (
                        "Only the organiser can cancel this meeting."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if meeting.status == Meeting.STATUS_CANCELLED:
            return Response(
                {"detail": "Meeting is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        meeting.cancel()
        return Response(MeetingDetailSerializer(meeting).data)


# ---------------------------------------------------------------------------

class MeetingExportICSView(APIView):
    """
    GET /api/meetings/{id}/export-ics/

    Manual APIView -- returns a raw file download (text/calendar),
    not a JSON response, so generics are not suitable here.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={(200, "text/calendar"): bytes},
        description="Export the meeting as an ICS calendar file.",
    )
    def get(self, request, pk):
        meeting = get_object_or_404(
            get_user_meetings(request.user), pk=pk
        )
        ics_content = generate_ics_for_meeting(meeting)

        safe_title = "".join(
            c if c.isalnum() else "_" for c in meeting.title
        )
        response = HttpResponse(
            ics_content, content_type="text/calendar"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{safe_title}.ics"'
        )
        return response


# ---------------------------------------------------------------------------

class MyCalendarView(APIView):
    """
    GET /api/meetings/my-calendar/

    Manual APIView -- returns a bulk ICS file download covering all
    upcoming meetings; not a standard list/detail operation.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={(200, "text/calendar"): bytes},
        description=(
            "Download all upcoming meetings as a single ICS file."
        ),
    )
    def get(self, request):
        meetings = get_user_meetings(request.user).filter(
            status=Meeting.STATUS_SCHEDULED,
            start_time__gte=timezone.now(),
        )
        ics_content = generate_ics_for_multiple_meetings(meetings)
        response = HttpResponse(
            ics_content, content_type="text/calendar"
        )
        response["Content-Disposition"] = (
            'attachment; filename="my_meetings.ics"'
        )
        return response


# ---------------------------------------------------------------------------

class ConflictCheckView(APIView):
    """
    POST /api/meetings/check-conflicts/

    Manual APIView -- takes a custom payload and runs a cross-meeting
    query; not tied to a single model instance.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ConflictCheckSerializer,
        responses={200: ConflictCheckSerializer},
        description=(
            "Check whether any of the given emails have "
            "scheduling conflicts."
        ),
    )
    def post(self, request):
        serializer = ConflictCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        conflicts = check_participants_conflicts(
            participants_emails=data["participant_emails"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            exclude_meeting_id=data.get("exclude_meeting_id"),
        )

        return Response(
            {
                "has_conflicts": bool(conflicts),
                "conflicts": conflicts,
            }
        )


# ---------------------------------------------------------------------------

class MeetingNotifyView(APIView):
    """
    POST /api/meetings/{id}/notify/

    Manual APIView -- triggers a side-effect (sends emails) rather
    than creating or modifying a resource.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Manually send notifications to all participants.",
        request=None,
    )
    def post(self, request, pk):
        meeting = get_object_or_404(
            get_user_meetings(request.user), pk=pk
        )

        if not is_meeting_owner(request.user, meeting):
            return Response(
                {
                    "detail": (
                        "Only the organiser can send notifications."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        notification_type = request.data.get("type", "reminder")
        allowed = [t[0] for t in MeetingNotification.TYPE_CHOICES]
        if notification_type not in allowed:
            return Response(
                {"detail": f"Type must be one of: {allowed}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = notify_all_participants(meeting, notification_type)
        return Response({"results": results})


# ===========================================================================
# Participant views
# ===========================================================================

class ParticipantListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/meetings/{meeting_id}/participants/   List participants.
    POST /api/meetings/{meeting_id}/participants/   Add a participant.

    Uses generics.ListCreateAPIView -- standard list + create pattern
    scoped to a parent meeting.
    """

    permission_classes = [IsAuthenticated]

    def _get_meeting(self):
        return get_object_or_404(
            Meeting, pk=self.kwargs["meeting_id"]
        )

    def get_queryset(self):
        return Participant.objects.filter(
            meeting=self._get_meeting()
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ParticipantCreateSerializer
        return ParticipantSerializer

    def perform_create(self, serializer):
        meeting = self._get_meeting()

        if not is_meeting_owner(self.request.user, meeting):
            raise PermissionDenied(
                "Only the organiser can add participants."
            )

        email = serializer.validated_data["email"]
        conflicts = check_participants_conflicts(
            participants_emails=[email],
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            exclude_meeting_id=meeting.id,
        )
        if conflicts:
            raise ValidationError(
                {
                    "conflict": (
                        f"{email} has a scheduling conflict."
                    ),
                    "details": conflicts,
                }
            )

        serializer.save(meeting=meeting)


# ---------------------------------------------------------------------------

class ParticipantDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/meetings/{meeting_id}/participants/{id}/

    Uses generics.DestroyAPIView -- single-object delete with
    ownership enforcement in perform_destroy.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        return Participant.objects.filter(
            meeting_id=self.kwargs["meeting_id"]
        )

    def perform_destroy(self, instance):
        if not is_meeting_owner(self.request.user, instance.meeting):
            raise PermissionDenied(
                "Only the organiser can remove participants."
            )
        instance.delete()


# ---------------------------------------------------------------------------

class ParticipantStatusView(APIView):
    """
    PATCH /api/meetings/{meeting_id}/participants/{id}/status/

    Manual APIView -- updates RSVP status using domain model methods
    (accept / decline) rather than a standard serializer save.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ParticipantStatusSerializer,
        responses={200: ParticipantSerializer},
        description=(
            "Update your own participation status "
            "(accept / decline / tentative)."
        ),
    )
    def patch(self, request, meeting_id, pk):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        participant = get_object_or_404(
            Participant, pk=pk, meeting=meeting
        )

        # A participant can only change their own status.
        # The meeting organiser may change any participant's status.
        if participant.user != request.user:
            if not is_meeting_owner(request.user, meeting):
                return Response(
                    {
                        "detail": (
                            "You can only update "
                            "your own participation status."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = ParticipantStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]

        if new_status == Participant.STATUS_ACCEPTED:
            participant.accept()
        elif new_status == Participant.STATUS_DECLINED:
            participant.decline()
        else:
            participant.status = new_status
            participant.responded_at = timezone.now()
            participant.save(
                update_fields=["status", "responded_at"]
            )

        return Response(ParticipantSerializer(participant).data)


# ===========================================================================
# Notification views
# ===========================================================================

class MeetingNotificationListView(generics.ListAPIView):
    """
    GET /api/meetings/{meeting_id}/notifications/

    Uses generics.ListAPIView -- read-only list, no create/update
    needed for the notification log.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MeetingNotificationSerializer

    def get_queryset(self):
        meeting = get_object_or_404(
            Meeting, pk=self.kwargs["meeting_id"]
        )
        return MeetingNotification.objects.filter(meeting=meeting)



