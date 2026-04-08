"""
Integración con Contactos.app de macOS.
Lee y escribe contactos mediante vCard y AppleScript.
"""
import subprocess

import vobject


def create_macos_contact(first_name, last_name, email="", phone="", company=""):
    """Crea un contacto en Contactos.app de macOS vía AppleScript."""
    script = f'''
    tell application "Contacts"
        set newPerson to make new person with properties {{first name:"{first_name}", last name:"{last_name}", organization:"{company}"}}
    '''
    if email:
        script += f'''
        make new email at end of emails of newPerson with properties {{label:"work", value:"{email}"}}
        '''
    if phone:
        script += f'''
        make new phone at end of phones of newPerson with properties {{label:"work", value:"{phone}"}}
        '''
    script += '''
        save
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout al crear contacto"


def search_macos_contacts(query):
    """Busca contactos en Contactos.app."""
    script = f'''
    tell application "Contacts"
        set matchingPeople to (every person whose name contains "{query}")
        set resultList to {{}}
        repeat with p in matchingPeople
            set fullName to (first name of p) & " " & (last name of p)
            set personEmail to ""
            if (count of emails of p) > 0 then
                set personEmail to value of first email of p
            end if
            set personPhone to ""
            if (count of phones of p) > 0 then
                set personPhone to value of first phone of p
            end if
            set end of resultList to fullName & "|" & personEmail & "|" & personPhone
        end repeat
        return resultList
    end tell
    '''
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            contacts = []
            for item in result.stdout.strip().split(", "):
                parts = item.split("|")
                contacts.append({
                    "name": parts[0] if len(parts) > 0 else "",
                    "email": parts[1] if len(parts) > 1 else "",
                    "phone": parts[2] if len(parts) > 2 else "",
                })
            return contacts
        return []
    except subprocess.TimeoutExpired:
        return []


def export_contact_to_vcard(contact):
    """Exporta un contacto del CRM a formato vCard."""
    j = vobject.vCard()
    j.add("n").value = vobject.vcard.Name(family=contact.last_name, given=contact.first_name)
    j.add("fn").value = contact.full_name
    if contact.email:
        j.add("email").value = contact.email
    if contact.phone:
        j.add("tel").value = contact.phone
    if contact.company:
        j.add("org").value = [contact.company.name]
    if contact.job_title:
        j.add("title").value = contact.job_title
    return j.serialize()
