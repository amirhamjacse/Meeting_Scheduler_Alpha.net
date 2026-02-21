"""
Conflict detection utility.

A conflict occurs when a participant (identified by email) is already
scheduled in another meeting whose time range overlaps with the
proposed meeting.
"""


def get_conflicting_meetings(
    email,
    start_time,
    end_time,
    exclude_meeting_id=None,
):
    """
    Return meetings where ``email`` is a participant AND the meeting's
    time range overlaps with [start_time, end_time].

    Overlap condition (A = existing meeting, B = proposed meeting)::

        A.start < B.end  AND  A.end > B.start

    Args:
        email: Participant email to check.
        start_time: Proposed meeting start (timezone-aware datetime).
        end_time: Proposed meeting end (timezone-aware datetime).
        exclude_meeting_id: UUID of a meeting to ignore (for updates).

    Returns:
        QuerySet of conflicting Meeting instances.
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


def check_participants_conflicts(
    participants_emails,
    start_time,
    end_time,
    exclude_meeting_id=None,
):
    """
    Check a list of email addresses for scheduling conflicts.

    Args:
        participants_emails: List of email strings to check.
        start_time: Proposed meeting start datetime.
        end_time: Proposed meeting end datetime.
        exclude_meeting_id: Optional meeting UUID to exclude.

    Returns:
        dict mapping email -> list of conflicting meeting dicts.
        Empty dict means no conflicts found.
    """
    conflicts = {}

    for email in participants_emails:
        conflicting = get_conflicting_meetings(
            email, start_time, end_time, exclude_meeting_id
        )
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
