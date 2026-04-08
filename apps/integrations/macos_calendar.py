"""
Integración con Calendario.app de macOS.
Lee y escribe eventos mediante archivos .ics en ~/Library/Calendars
y/o AppleScript con la app Calendario nativa.
"""
import subprocess
import os
from pathlib import Path
from datetime import datetime

from django.conf import settings
from icalendar import Calendar, Event


def get_calendar_path():
    return Path(os.path.expanduser(settings.MACOS_CALENDAR_PATH))


def create_calendar_event(title, start_dt, end_dt, location="", notes="", calendar_name="CRM"):
    """Crea un evento en Calendario.app de macOS vía AppleScript."""
    start_str = start_dt.strftime("%B %d, %Y %I:%M:%S %p")
    end_str = end_dt.strftime("%B %d, %Y %I:%M:%S %p")

    script = f'''
    tell application "Calendar"
        tell calendar "{calendar_name}"
            set newEvent to make new event with properties {{summary:"{title}", start date:date "{start_str}", end date:date "{end_str}", location:"{location}", description:"{notes}"}}
        end tell
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout al crear evento"


def get_today_events(calendar_name="CRM"):
    """Obtiene los eventos de hoy desde Calendario.app."""
    script = f'''
    tell application "Calendar"
        set today to current date
        set time of today to 0
        set tomorrow to today + (1 * days)
        set eventList to {{}}
        tell calendar "{calendar_name}"
            set todayEvents to (every event whose start date >= today and start date < tomorrow)
            repeat with anEvent in todayEvents
                set end of eventList to (summary of anEvent) & "|" & ((start date of anEvent) as string) & "|" & ((end date of anEvent) as string)
            end repeat
        end tell
        return eventList
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            events = []
            for item in result.stdout.strip().split(", "):
                parts = item.split("|")
                if len(parts) >= 1:
                    events.append({"title": parts[0], "start": parts[1] if len(parts) > 1 else "", "end": parts[2] if len(parts) > 2 else ""})
            return events
        return []
    except subprocess.TimeoutExpired:
        return []


def export_activity_to_ics(activity):
    """Exporta una actividad del CRM a un archivo .ics."""
    cal = Calendar()
    cal.add("prodid", "-//TALENTO SOSTENIBLE CRM//")
    cal.add("version", "2.0")

    event = Event()
    event.add("summary", activity.subject)
    event.add("description", activity.description)
    if activity.due_date:
        event.add("dtstart", activity.due_date)
    cal.add_component(event)

    return cal.to_ical()
