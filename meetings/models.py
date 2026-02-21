import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Meeting(models.Model):
    """Represents a scheduled meeting created by a user."""

    STATUS_SCHEDULED = "scheduled"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_COMPLETED, "Completed"),
    ]

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_meetings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["start_time", "end_time"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_time:%Y-%m-%d %H:%M})"

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    "End time must be after start time."
                )

    def duration_minutes(self):
        """Return the meeting duration in whole minutes."""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return 0

    def is_upcoming(self):
        """Return True if the meeting is still in the future."""
        return (
            self.start_time > timezone.now()
            and self.status == self.STATUS_SCHEDULED
        )

    def cancel(self):
        """Mark the meeting as cancelled and persist the change."""
        self.status = self.STATUS_CANCELLED
        self.save(update_fields=["status", "updated_at"])


class Participant(models.Model):
    """A person invited to a meeting, identified by email."""

    STATUS_INVITED = "invited"
    STATUS_ACCEPTED = "accepted"
    STATUS_DECLINED = "declined"
    STATUS_TENTATIVE = "tentative"

    STATUS_CHOICES = [
        (STATUS_INVITED, "Invited"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_DECLINED, "Declined"),
        (STATUS_TENTATIVE, "Tentative"),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="participants",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meeting_participations",
    )
    email = models.EmailField()
    name = models.CharField(max_length=150, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_INVITED,
    )
    invited_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("meeting", "email")
        ordering = ["invited_at"]

    def __str__(self):
        return (
            f"{self.email} -> {self.meeting.title} [{self.status}]"
        )

    def accept(self):
        """Record an accepted RSVP."""
        self.status = self.STATUS_ACCEPTED
        self.responded_at = timezone.now()
        self.save(update_fields=["status", "responded_at"])

    def decline(self):
        """Record a declined RSVP."""
        self.status = self.STATUS_DECLINED
        self.responded_at = timezone.now()
        self.save(update_fields=["status", "responded_at"])


class MeetingNotification(models.Model):
    """Log of every notification email sent for a meeting."""

    TYPE_INVITATION = "invitation"
    TYPE_UPDATE = "update"
    TYPE_CANCELLATION = "cancellation"
    TYPE_REMINDER = "reminder"

    TYPE_CHOICES = [
        (TYPE_INVITATION, "Invitation"),
        (TYPE_UPDATE, "Meeting Updated"),
        (TYPE_CANCELLATION, "Meeting Cancelled"),
        (TYPE_REMINDER, "Reminder"),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    email = models.EmailField()
    notification_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES
    )
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return (
            f"[{self.notification_type}] -> "
            f"{self.email} | {self.meeting.title}"
        )
