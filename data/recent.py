import json
import os
from data.paths import get_data_dir

RECENT_FILE = os.path.join(get_data_dir(), "recent.json")
MAX_RECENT = 20

def cargar_recientes():
    if os.path.exists(RECENT_FILE):
        try:
            with open(RECENT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def guardar_recientes(recientes):
    with open(RECENT_FILE, "w", encoding="utf-8") as f:
        json.dump(recientes, f, ensure_ascii=False, indent=2)

def añadir_reciente(ruta, titulo=None, artista=None):
    recientes = cargar_recientes()
    entry = {"path": ruta}
    if titulo:
        entry["title"] = titulo
    if artista:
        entry["artist"] = artista
    # remove duplicate by path
    for i in range(len(recientes) - 1, -1, -1):
        e = recientes[i]
        e_path = e if isinstance(e, str) else e.get("path", "")
        if e_path == ruta:
            recientes.pop(i)
    recientes.insert(0, entry)
    recientes = recientes[:MAX_RECENT]
    guardar_recientes(recientes)

def obtener_info_reciente(entry):
    """Extrae path, título y artista de una entrada de recientes (compatible con viejo formato)."""
    if isinstance(entry, str):
        return entry, None, None
    return entry.get("path", ""), entry.get("title"), entry.get("artist")
