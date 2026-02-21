"""
Conflict detection utility.

A conflict occurs when a participant (identified by email) is already
scheduled in another meeting whose time range overlaps with a proposed meeting.
"""

from django.db.models import Q


def get_conflicting_meetings(email: str, start_time, end_time, exclude_meeting_id=None):
    """
    Return meetings where `email` is a participant AND the meeting's
    time range overlaps with [start_time, end_time].

    Overlap condition (A = existing meeting, B = new meeting):
        A.start < B.end  AND  A.end > B.start

    Args:
        email: Participant email to check
        start_time: Proposed meeting start (timezone-aware datetime)
        end_time: Proposed meeting end (timezone-aware datetime)
        exclude_meeting_id: UUID of a meeting to ignore (for updates)

    Returns:
        QuerySet of conflicting Meeting instances
    """
    from meetings.models import Meeting

    qs = Meeting.objects.filter(
        participants__email=email,
        status=Meeting.STATUS_SCHEDULED,
        start_time__lt=end_time,
        end_time__gt=start_time,
    ).distinct()

    if exclude_meeting_id:
        qs = qs.exclude(id=exclude_meeting_id)

    return qs


def check_participants_conflicts(participants_emails, start_time, end_time, exclude_meeting_id=None):
    """
    Check a list of emails for conflicts.

    Returns:
        dict mapping email -> list of conflicting meeting dicts
    """
    conflicts = {}
    for email in participants_emails:
        conflicting = get_conflicting_meetings(email, start_time, end_time, exclude_meeting_id)
        if conflicting.exists():
            conflicts[email] = [
                {
                    "id": str(m.id),
                    "title": m.title,
                    "start_time": m.start_time.isoformat(),
                    "end_time": m.end_time.isoformat(),
                }
                for m in conflicting
            ]
    return conflicts
