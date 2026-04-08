"""
Integración con Teléfono/FaceTime de macOS.
Inicia llamadas vía AppleScript y el protocolo tel://.
"""
import subprocess


def make_phone_call(phone_number):
    """Inicia una llamada de teléfono a través de FaceTime en macOS."""
    clean_number = "".join(c for c in phone_number if c.isdigit() or c == "+")
    try:
        result = subprocess.run(
            ["open", f"tel:{clean_number}"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout al iniciar llamada"


def make_facetime_call(contact_id_or_number):
    """Inicia una videollamada FaceTime."""
    try:
        result = subprocess.run(
            ["open", f"facetime:{contact_id_or_number}"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout al iniciar FaceTime"


def send_imessage(phone_number, message):
    """Envía un iMessage vía AppleScript."""
    clean_number = "".join(c for c in phone_number if c.isdigit() or c == "+")
    script = f'''
    tell application "Messages"
        set targetService to 1st account whose service type = iMessage
        set targetBuddy to participant "{clean_number}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout al enviar mensaje"
