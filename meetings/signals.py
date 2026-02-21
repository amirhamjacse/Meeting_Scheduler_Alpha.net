"""
Django signals for the meetings app.
Automatically trigger notifications when meeting status changes.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Meeting, Participant


@receiver(post_save, sender=Participant)
def notify_on_participant_added(sender, instance, created, **kwargs):
    """Send invitation notification when a new participant is added."""
    if created:
        from .utils.notifications import send_meeting_notification
        send_meeting_notification(instance, instance.meeting, "invitation")


@receiver(pre_save, sender=Meeting)
def notify_on_meeting_cancelled(sender, instance, **kwargs):
    """Send cancellation notification when a meeting is cancelled."""
    if not instance.pk:
        return  # New meeting, skip

    try:
        old = Meeting.objects.get(pk=instance.pk)
    except Meeting.DoesNotExist:
        return

    if old.status != Meeting.STATUS_CANCELLED and instance.status == Meeting.STATUS_CANCELLED:
        from .utils.notifications import notify_all_participants
        notify_all_participants(old, "cancellation")

    elif old.status == Meeting.STATUS_SCHEDULED and instance.status == Meeting.STATUS_SCHEDULED:
        fields_changed = (
            old.start_time != instance.start_time
            or old.end_time != instance.end_time
            or old.location != instance.location
            or old.title != instance.title
        )
        if fields_changed:
            from .utils.notifications import notify_all_participants
            notify_all_participants(old, "update")
