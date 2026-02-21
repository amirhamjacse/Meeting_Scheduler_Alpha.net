from django.urls import path

from .views import (
    ConflictCheckView,
    MeetingCancelView,
    MeetingDetailView,
    MeetingExportICSView,
    MeetingListCreateView,
    MeetingNotificationListView,
    MeetingNotifyView,
    MyCalendarView,
    ParticipantDeleteView,
    ParticipantListCreateView,
    ParticipantStatusView,
)

urlpatterns = [

    # ------------------------------------------------------------------
    # Meeting endpoints
    # ------------------------------------------------------------------

    # List all meetings / create a new meeting
    path(
        "meetings/",
        MeetingListCreateView.as_view(),
        name="meeting-list-create",
    ),

    # These two detail-less actions must come BEFORE <uuid:pk>/ so the
    # URL router does not try to match "my-calendar" as a UUID.
    path(
        "meetings/my-calendar/",
        MyCalendarView.as_view(),
        name="meeting-my-calendar",
    ),
    path(
        "meetings/check-conflicts/",
        ConflictCheckView.as_view(),
        name="meeting-check-conflicts",
    ),

    # Retrieve / update / delete a single meeting
    path(
        "meetings/<uuid:pk>/",
        MeetingDetailView.as_view(),
        name="meeting-detail",
    ),

    # Cancel a meeting
    path(
        "meetings/<uuid:pk>/cancel/",
        MeetingCancelView.as_view(),
        name="meeting-cancel",
    ),

    # Export a single meeting as an ICS file
    path(
        "meetings/<uuid:pk>/export-ics/",
        MeetingExportICSView.as_view(),
        name="meeting-export-ics",
    ),

    # Send notifications to all participants
    path(
        "meetings/<uuid:pk>/notify/",
        MeetingNotifyView.as_view(),
        name="meeting-notify",
    ),

    # ------------------------------------------------------------------
    # Participant endpoints
    # ------------------------------------------------------------------

    # List participants / add a participant
    path(
        "meetings/<uuid:meeting_id>/participants/",
        ParticipantListCreateView.as_view(),
        name="participant-list-create",
    ),

    # Remove a participant
    path(
        "meetings/<uuid:meeting_id>/participants/<int:pk>/",
        ParticipantDeleteView.as_view(),
        name="participant-delete",
    ),

    # Update a participant's RSVP status
    path(
        "meetings/<uuid:meeting_id>/participants/<int:pk>/status/",
        ParticipantStatusView.as_view(),
        name="participant-status",
    ),

    # ------------------------------------------------------------------
    # Notification endpoints
    # ------------------------------------------------------------------

    # Read-only log of notifications sent for a meeting
    path(
        "meetings/<uuid:meeting_id>/notifications/",
        MeetingNotificationListView.as_view(),
        name="meeting-notification-list",
    ),
]

