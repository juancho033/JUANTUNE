# data/database.py
import json
import os
from data.paths import get_data_dir

PLAYLISTS_FILE = os.path.join(get_data_dir(), "playlists.json")

def cargar_playlists():
    """Carga las playlists desde el archivo JSON."""
    if os.path.exists(PLAYLISTS_FILE):
        try:
            with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"playlists": []}
    return {"playlists": []}

def guardar_playlists(data):
    """Guarda las playlists en el archivo JSON."""
    with open(PLAYLISTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def obtener_playlists():
    """Retorna la lista de nombres de playlists."""
    data = cargar_playlists()
    return [p["name"] for p in data["playlists"]]

def obtener_canciones_playlist(nombre):
    """Retorna las canciones de una playlist específica."""
    data = cargar_playlists()
    for p in data["playlists"]:
        if p["name"] == nombre:
            return p["songs"]
    return []

def crear_playlist(nombre):
    """Crea una nueva playlist vacía."""
    data = cargar_playlists()
    data["playlists"].append({"name": nombre, "songs": []})
    guardar_playlists(data)

def añadir_cancion_playlist(nombre_playlist, ruta_cancion):
    """Añade una canción a una playlist existente."""
    data = cargar_playlists()
    for p in data["playlists"]:
        if p["name"] == nombre_playlist:
            if ruta_cancion not in p["songs"]:
                p["songs"].append(ruta_cancion)
            break
    guardar_playlists(data)

def eliminar_playlist(nombre):
    """Elimina una playlist."""
    data = cargar_playlists()
    data["playlists"] = [p for p in data["playlists"] if p["name"] != nombre]
    guardar_playlists(data)
