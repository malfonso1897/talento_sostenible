"""
Gestión de archivos locales del CRM.
Almacena y organiza documentos en ~/Documents/TalentoSostenible/Archivos.
"""
import os
import shutil
from pathlib import Path

from django.conf import settings


def get_files_dir():
    path = Path(os.path.expanduser(settings.CRM_FILES_DIR))
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_entity_folder(entity_type, entity_id):
    """Obtiene (o crea) la carpeta de archivos de una entidad."""
    folder = get_files_dir() / entity_type / str(entity_id)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_file(entity_type, entity_id, uploaded_file):
    """Guarda un archivo subido en la carpeta de la entidad."""
    folder = get_entity_folder(entity_type, entity_id)
    file_path = folder / uploaded_file.name

    # Evitar sobreescritura
    counter = 1
    while file_path.exists():
        stem = Path(uploaded_file.name).stem
        suffix = Path(uploaded_file.name).suffix
        file_path = folder / f"{stem}_{counter}{suffix}"
        counter += 1

    with open(file_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    return str(file_path)


def list_files(entity_type, entity_id):
    """Lista los archivos de una entidad."""
    folder = get_entity_folder(entity_type, entity_id)
    files = []
    for item in folder.iterdir():
        if item.is_file():
            files.append({
                "name": item.name,
                "path": str(item),
                "size": item.stat().st_size,
                "modified": item.stat().st_mtime,
            })
    return sorted(files, key=lambda x: x["modified"], reverse=True)


def delete_file(file_path):
    """Elimina un archivo."""
    path = Path(file_path)
    if path.exists() and path.is_file():
        # Verificar que está dentro de la carpeta de archivos del CRM
        files_dir = get_files_dir()
        if files_dir in path.parents or path.parent == files_dir:
            path.unlink()
            return True
    return False


def open_in_finder(entity_type, entity_id):
    """Abre la carpeta de una entidad en Finder."""
    folder = get_entity_folder(entity_type, entity_id)
    os.system(f'open "{folder}"')
