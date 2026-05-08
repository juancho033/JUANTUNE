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
        except:
            return []
    return []

def guardar_recientes(recientes):
    with open(RECENT_FILE, "w", encoding="utf-8") as f:
        json.dump(recientes, f, ensure_ascii=False, indent=2)

def añadir_reciente(ruta):
    recientes = cargar_recientes()
    if ruta in recientes:
        recientes.remove(ruta)
    recientes.insert(0, ruta)
    recientes = recientes[:MAX_RECENT]
    guardar_recientes(recientes)
