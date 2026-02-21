"""
Notification utility.

In development the default EMAIL_BACKEND prints emails to the console.
In production, swap EMAIL_BACKEND to an SMTP or transactional provider
(SendGrid, Mailgun, etc.) in your .env file -- no code changes needed.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------

TEMPLATES = {
    "invitation": {
        "subject": "You have been invited to: {title}",
        "body": (
            "Hi {name},\n\n"
            "You have been invited to the following meeting:\n\n"
            "Title:       {title}\n"
            "Description: {description}\n"
            "Location:    {location}\n"
            "Start:       {start_time}\n"
            "End:         {end_time}\n\n"
            "Please respond to confirm your attendance.\n\n"
            "Best regards,\nMeeting Scheduler"
        ),
    },
    "update": {
        "subject": "Meeting updated: {title}",
        "body": (
            "Hi {name},\n\n"
            "The following meeting has been updated:\n\n"
            "Title:    {title}\n"
            "Location: {location}\n"
            "Start:    {start_time}\n"
            "End:      {end_time}\n\n"
            "Best regards,\nMeeting Scheduler"
        ),
    },
    "cancellation": {
        "subject": "Meeting cancelled: {title}",
        "body": (
            "Hi {name},\n\n"
            "The following meeting has been CANCELLED:\n\n"
            "Title:         {title}\n"
            "Was scheduled: {start_time}\n\n"
            "Best regards,\nMeeting Scheduler"
        ),
    },
    "reminder": {
        "subject": "Reminder: {title} starts soon",
        "body": (
            "Hi {name},\n\n"
            "This is a reminder that the meeting below starts soon:\n\n"
            "Title:    {title}\n"
            "Location: {location}\n"
            "Start:    {start_time}\n\n"
            "Best regards,\nMeeting Scheduler"
        ),
    },
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _render(template_key, context):
    """Return (subject, body) for the given template key and context."""
    tmpl = TEMPLATES.get(template_key, TEMPLATES["invitation"])
    subject = tmpl["subject"].format(**context)
    body = tmpl["body"].format(**context)
    return subject, body


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_meeting_notification(participant, meeting, notification_type):
    """
    Send (or simulate) a notification email to one participant.

    Creates a MeetingNotification log entry regardless of whether the
    send succeeds, recording any error for later inspection.

    Args:
        participant: Participant model instance.
        meeting: Meeting model instance.
        notification_type: One of invitation / update /
                           cancellation / reminder.

    Returns:
        bool: True if the email was sent successfully.
    """
    from meetings.models import MeetingNotification

    context = {
        "name": participant.name or participant.email,
        "title": meeting.title,
        "description": meeting.description or "-",
        "location": meeting.location or "-",
        "start_time": meeting.start_time.strftime(
            "%Y-%m-%d %H:%M UTC"
        ),
        "end_time": meeting.end_time.strftime("%Y-%m-%d %H:%M UTC"),
    }

    subject, body = _render(notification_type, context)

    notif = MeetingNotification.objects.create(
        meeting=meeting,
        participant=participant,
        email=participant.email,
        notification_type=notification_type,
        message=body,
        is_sent=False,
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant.email],
            fail_silently=False,
        )
        notif.is_sent = True
        notif.save(update_fields=["is_sent"])
        logger.info(
            "Notification '%s' sent to %s",
            notification_type,
            participant.email,
        )
        return True
    except Exception as exc:
        notif.error_message = str(exc)
        notif.save(update_fields=["error_message"])
        logger.warning(
            "Failed to send notification '%s' to %s: %s",
            notification_type,
            participant.email,
            exc,
        )
        return False


def notify_all_participants(meeting, notification_type):
    """
    Send the given notification type to every participant.

    Returns:
        dict mapping participant email -> bool (success/failure).
    """
    results = {}
    for participant in meeting.participants.all():
        results[participant.email] = send_meeting_notification(
            participant, meeting, notification_type
        )
    return results
