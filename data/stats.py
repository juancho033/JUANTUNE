import json
import os
import time
from data.paths import get_data_dir

STATS_FILE = os.path.join(get_data_dir(), "stats.json")

def cargar_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_stats(stats):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def registrar_reproduccion(ruta, duracion):
    stats = cargar_stats()
    if ruta not in stats:
        stats[ruta] = {"plays": 0, "total_time": 0, "last_played": 0}
    stats[ruta]["plays"] += 1
    stats[ruta]["total_time"] += duracion
    stats[ruta]["last_played"] = time.time()
    guardar_stats(stats)

def obtener_top(tope=10):
    stats = cargar_stats()
    ordenados = sorted(stats.items(), key=lambda x: x[1]["plays"], reverse=True)
    return ordenados[:tope]

def total_plays():
    stats = cargar_stats()
    return sum(s["plays"] for s in stats.values())

def total_time():
    stats = cargar_stats()
    return sum(s["total_time"] for s in stats.values())

def unique_songs():
    return len(cargar_stats())
