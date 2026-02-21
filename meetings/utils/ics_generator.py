"""
ICS (iCalendar) file generator.

Uses the icalendar library to produce RFC 5545-compliant .ics files
compatible with Google Calendar, Outlook, Apple Calendar, etc.
"""

from django.utils import timezone
from icalendar import Calendar, Event, vCalAddress, vText


def generate_ics_for_meeting(meeting):
    """
    Generate an ICS file for a single Meeting instance.

    Args:
        meeting: Meeting model instance.

    Returns:
        bytes: RFC 5545-compliant ICS content.
    """
    cal = Calendar()
    cal.add("prodid", "-//Meeting Scheduler//meeting-scheduler//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "REQUEST")

    event = Event()
    event.add("summary", meeting.title)
    event.add("description", meeting.description or "")
    event.add("location", meeting.location or "")
    event.add("dtstart", meeting.start_time)
    event.add("dtend", meeting.end_time)
    event.add("dtstamp", timezone.now())
    event.add("uid", str(meeting.id))
    event.add("status", _map_status(meeting.status))
    event.add("created", meeting.created_at)
    event.add("last-modified", meeting.updated_at)

    # Add organiser
    organizer_email = meeting.created_by.email
    organizer_name = (
        meeting.created_by.username or meeting.created_by.email
    )
    organizer = vCalAddress(f"MAILTO:{organizer_email}")
    organizer.params["cn"] = vText(organizer_name)
    organizer.params["role"] = vText("CHAIR")
    event["organizer"] = organizer

    # Add attendees (participants)
    for participant in meeting.participants.all():
        attendee = vCalAddress(f"MAILTO:{participant.email}")
        attendee.params["cn"] = vText(
            participant.name or participant.email
        )
        attendee.params["role"] = vText("REQ-PARTICIPANT")
        attendee.params["partstat"] = vText(
            _map_participant_status(participant.status)
        )
        attendee.params["rsvp"] = vText("TRUE")
        event.add("attendee", attendee, encode=0)

    cal.add_component(event)
    return cal.to_ical()


def generate_ics_for_multiple_meetings(meetings):
    """
    Generate a single ICS file that contains multiple meeting events.

    Args:
        meetings: QuerySet or list of Meeting instances.

    Returns:
        bytes: RFC 5545-compliant ICS content.
    """
    cal = Calendar()
    cal.add("prodid", "-//Meeting Scheduler//meeting-scheduler//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")

    for meeting in meetings:
        event = Event()
        event.add("summary", meeting.title)
        event.add("description", meeting.description or "")
        event.add("location", meeting.location or "")
        event.add("dtstart", meeting.start_time)
        event.add("dtend", meeting.end_time)
        event.add("dtstamp", timezone.now())
        event.add("uid", str(meeting.id))
        event.add("status", _map_status(meeting.status))
        cal.add_component(event)

    return cal.to_ical()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _map_status(status):
    """Convert a Meeting status string to an RFC 5545 STATUS value."""
    mapping = {
        "scheduled": "CONFIRMED",
        "cancelled": "CANCELLED",
        "completed": "COMPLETED",
    }
    return mapping.get(status, "CONFIRMED")


def _map_participant_status(status):
    """Convert a Participant status to an RFC 5545 PARTSTAT value."""
    mapping = {
        "invited": "NEEDS-ACTION",
        "accepted": "ACCEPTED",
        "declined": "DECLINED",
        "tentative": "TENTATIVE",
    }
    return mapping.get(status, "NEEDS-ACTION")
