from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import Meeting, Participant, MeetingNotification
from .serializers import (
    MeetingListSerializer,
    MeetingDetailSerializer,
    MeetingCreateSerializer,
    ParticipantSerializer,
    ParticipantCreateSerializer,
    ParticipantStatusSerializer,
    ConflictCheckSerializer,
    MeetingNotificationSerializer,
)
from .utils.ics_generator import generate_ics_for_meeting, generate_ics_for_multiple_meetings
from .utils.conflict_detector import check_participants_conflicts
from .utils.notifications import notify_all_participants


# ──────────────────────────────────────────────
# Permissions helpers
# ──────────────────────────────────────────────

def is_meeting_owner(user, meeting):
    return meeting.created_by == user


# ──────────────────────────────────────────────
# Meeting ViewSet
# ──────────────────────────────────────────────

class MeetingViewSet(viewsets.ModelViewSet):
    """
    CRUD for meetings.

    list      GET  /api/meetings/
    create    POST /api/meetings/
    retrieve  GET  /api/meetings/{id}/
    update    PUT  /api/meetings/{id}/
    partial   PATCH /api/meetings/{id}/
    destroy   DELETE /api/meetings/{id}/

    Extra actions:
      POST /api/meetings/{id}/cancel/
      GET  /api/meetings/{id}/export-ics/
      GET  /api/meetings/my-calendar/
      POST /api/meetings/check-conflicts/
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "location"]
    ordering_fields = ["start_time", "end_time", "created_at", "title"]
    ordering = ["start_time"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Meeting.objects.filter(
                # Meetings created by user OR where user is a participant
                created_by=user
            )
            | Meeting.objects.filter(participants__user=user)
        ).distinct().prefetch_related("participants")
        
        # Filter by status
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        # Filter by date range
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")
        if from_date:
            qs = qs.filter(start_time__date__gte=from_date)
        if to_date:
            qs = qs.filter(end_time__date__lte=to_date)

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return MeetingListSerializer
        if self.action in ("create", "update", "partial_update"):
            return MeetingCreateSerializer
        return MeetingDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if not is_meeting_owner(self.request.user, self.get_object()):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the meeting organiser can edit it.")
        serializer.save()

    def perform_destroy(self, instance):
        if not is_meeting_owner(self.request.user, instance):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the meeting organiser can delete it.")
        instance.delete()

    # ── Cancel ──────────────────────────────────
    @extend_schema(
        responses={200: MeetingDetailSerializer},
        description="Cancel a meeting and notify all participants.",
    )
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        meeting = self.get_object()
        if not is_meeting_owner(request.user, meeting):
            return Response(
                {"detail": "Only the organiser can cancel this meeting."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if meeting.status == Meeting.STATUS_CANCELLED:
            return Response(
                {"detail": "Meeting is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        meeting.cancel()
        return Response(MeetingDetailSerializer(meeting).data)

    # ── Export ICS ──────────────────────────────
    @extend_schema(
        responses={(200, "text/calendar"): bytes},
        description="Export meeting as an ICS calendar file.",
    )
    @action(detail=True, methods=["get"], url_path="export-ics")
    def export_ics(self, request, pk=None):
        meeting = self.get_object()
        ics_content = generate_ics_for_meeting(meeting)
        response = HttpResponse(ics_content, content_type="text/calendar")
        safe_title = "".join(c if c.isalnum() else "_" for c in meeting.title)
        response["Content-Disposition"] = f'attachment; filename="{safe_title}.ics"'
        return response

    # ── My Calendar (bulk ICS) ───────────────────
    @extend_schema(
        responses={(200, "text/calendar"): bytes},
        description="Download all your upcoming meetings as a single ICS file.",
    )
    @action(detail=False, methods=["get"], url_path="my-calendar")
    def my_calendar(self, request):
        meetings = self.get_queryset().filter(
            status=Meeting.STATUS_SCHEDULED,
            start_time__gte=timezone.now(),
        )
        ics_content = generate_ics_for_multiple_meetings(meetings)
        response = HttpResponse(ics_content, content_type="text/calendar")
        response["Content-Disposition"] = 'attachment; filename="my_meetings.ics"'
        return response

    # ── Conflict Check ───────────────────────────
    @extend_schema(
        request=ConflictCheckSerializer,
        responses={200: ConflictCheckSerializer},
        description="Check whether any of the provided emails have scheduling conflicts.",
    )
    @action(detail=False, methods=["post"], url_path="check-conflicts")
    def check_conflicts(self, request):
        serializer = ConflictCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        conflicts = check_participants_conflicts(
            participants_emails=data["participant_emails"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            exclude_meeting_id=data.get("exclude_meeting_id"),
        )

        has_conflicts = bool(conflicts)
        return Response(
            {
                "has_conflicts": has_conflicts,
                "conflicts": conflicts,
            }
        )

    # ── Send Notifications ───────────────────────
    @extend_schema(
        description="Manually trigger notifications to all participants.",
        request=None,
    )
    @action(detail=True, methods=["post"], url_path="notify")
    def notify(self, request, pk=None):
        meeting = self.get_object()
        if not is_meeting_owner(request.user, meeting):
            return Response(
                {"detail": "Only the organiser can send notifications."},
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


# ──────────────────────────────────────────────
# Participant ViewSet
# ──────────────────────────────────────────────

class ParticipantViewSet(viewsets.ModelViewSet):
    """
    Manage participants for a specific meeting.

    list   GET  /api/meetings/{meeting_pk}/participants/
    create POST /api/meetings/{meeting_pk}/participants/
    delete DELETE /api/meetings/{meeting_pk}/participants/{id}/
    update-status PATCH /api/meetings/{meeting_pk}/participants/{id}/status/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ParticipantSerializer

    def _get_meeting(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Meeting, pk=self.kwargs["meeting_pk"])

    def get_queryset(self):
        meeting = self._get_meeting()
        return Participant.objects.filter(meeting=meeting)

    def get_serializer_class(self):
        if self.action == "create":
            return ParticipantCreateSerializer
        if self.action == "update_status":
            return ParticipantStatusSerializer
        return ParticipantSerializer

    def perform_create(self, serializer):
        meeting = self._get_meeting()

        # Only organiser can add participants
        if not is_meeting_owner(self.request.user, meeting):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the organiser can add participants.")

        email = serializer.validated_data["email"]

        # Conflict check for new participant
        conflicts = check_participants_conflicts(
            participants_emails=[email],
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            exclude_meeting_id=meeting.id,
        )

        if conflicts:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                {
                    "conflict": f"{email} has a scheduling conflict.",
                    "details": conflicts,
                }
            )

        serializer.save(meeting=meeting)

    @extend_schema(
        request=ParticipantStatusSerializer,
        responses={200: ParticipantSerializer},
        description="Update your own participation status (accept/decline/tentative).",
    )
    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, meeting_pk=None, pk=None):
        participant = self.get_object()

        # Participants can only update their own status
        if participant.user != request.user:
            # Allow organiser too
            meeting = self._get_meeting()
            if not is_meeting_owner(request.user, meeting):
                return Response(
                    {"detail": "You can only update your own participation status."},
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
            participant.save(update_fields=["status", "responded_at"])

        return Response(ParticipantSerializer(participant).data)


# ──────────────────────────────────────────────
# Notification List (read-only)
# ──────────────────────────────────────────────

class MeetingNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only list of notifications for a meeting.
    GET /api/meetings/{meeting_pk}/notifications/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MeetingNotificationSerializer

    def get_queryset(self):
        from django.shortcuts import get_object_or_404
        meeting = get_object_or_404(Meeting, pk=self.kwargs["meeting_pk"])
        return MeetingNotification.objects.filter(meeting=meeting)
