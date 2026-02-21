"""
Django signals for the meetings app.

Automatically sends notification emails when:
- A participant is added to a meeting (invitation)
- A meeting is cancelled
- A scheduled meeting's key details change (update)
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Meeting, Participant


@receiver(post_save, sender=Participant)
def notify_on_participant_added(sender, instance, created, **kwargs):
    """Send an invitation email when a participant is first added."""
    if created:
        from .utils.notifications import send_meeting_notification
        send_meeting_notification(
            instance, instance.meeting, "invitation"
        )


@receiver(pre_save, sender=Meeting)
def notify_on_meeting_status_change(sender, instance, **kwargs):
    """
    Send notifications when a meeting is cancelled or updated.

    - Cancellation: notifies all participants.
    - Update: notifies if title, location, or times change.
    """
    if not instance.pk:
        # This is a brand-new meeting; nothing to compare against.
        return

    try:
        previous = Meeting.objects.get(pk=instance.pk)
    except Meeting.DoesNotExist:
        return

    from .utils.notifications import notify_all_participants

    being_cancelled = (
        previous.status != Meeting.STATUS_CANCELLED
        and instance.status == Meeting.STATUS_CANCELLED
    )
    if being_cancelled:
        notify_all_participants(previous, "cancellation")
        return

    # Both old and new are still scheduled -- check for content changes.
    both_scheduled = (
        previous.status == Meeting.STATUS_SCHEDULED
        and instance.status == Meeting.STATUS_SCHEDULED
    )
    if both_scheduled:
        details_changed = (
            previous.start_time != instance.start_time
            or previous.end_time != instance.end_time
            or previous.location != instance.location
            or previous.title != instance.title
        )
        if details_changed:
            notify_all_participants(previous, "update")
