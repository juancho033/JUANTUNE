#!/usr/bin/env python3
"""Script de administración para subir canciones a JuanTune Cloud.
Uso: python admin_upload.py o arrastra un MP3 encima."""
import os, sys
from services.cloudinary_service import upload_mp3
from services.drive_service import upload_mp3 as upload_drive
from services.firebase_service import add_song

def subir(ruta):
    nombre = os.path.basename(ruta).replace(".mp3", "")
    print(f"\n📄 Archivo: {nombre}")
    titulo = input("  Título: ").strip() or nombre
    artista = input("  Artista: ").strip() or "Desconocido"

    print(f"  ☁️  Subiendo a Cloudinary...")
    info = upload_mp3(ruta)
    duracion = int(float(info["duration"]))
    m, s = duracion // 60, duracion % 60
    print(f"  ✅ Subido (duración: {m}:{s:02d})")

    print(f"  📤 Subiendo a Google Drive...")
    drive_info = upload_drive(ruta)
    print(f"  ✅ Subido a Drive")

    data = {
        "title": titulo,
        "artist": artista,
        "duration": duracion,
        "cloudinary_url": info["url"],
        "cloudinary_public_id": info["public_id"],
        "download_url": drive_info["download_url"],
    }
    song_id = add_song(data)
    print(f"  ✅ Guardado en Firestore (id: {song_id})")
    print(f"  🌐 Streaming: {info['url']}")
    print(f"  ⬇️  Descarga: {drive_info['download_url']}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.lower().endswith(".mp3"):
                subir(arg)
    else:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        rutas = filedialog.askopenfilenames(title="Seleccionar MP3 para subir",
                                            filetypes=[("MP3", "*.mp3")])
        root.destroy()
        if rutas:
            for r in rutas:
                subir(r)
        else:
            print("No se seleccionó ningún archivo.")
