import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import os
import io
import time
from PIL import Image

class ReproductorAudio:
    def __init__(self):
        pygame.mixer.init()
        self.cancion_actual = None
        self.en_pausa = False
        self.posicion_base = 0
        self.duracion = 0
        self.volumen = 0.5
        self.tiempo_inicio_reproduccion = 0
        pygame.mixer.music.set_volume(self.volumen)

    def reiniciar_mixer(self):
        try:
            pygame.mixer.music.stop()
            if hasattr(pygame.mixer.music, 'unload'):
                pygame.mixer.music.unload()
            pygame.mixer.quit()
            time.sleep(0.05)
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volumen)
        except Exception as e:
            print(f"Mixer error: {e}")

    def cargar_cancion(self, ruta_archivo):
        if not os.path.exists(ruta_archivo) or os.path.getsize(ruta_archivo) == 0:
            return False
        try:
            audio = MP3(ruta_archivo)
            duracion = audio.info.length
        except Exception as e:
            print(f"MP3 error: {e}")
            return False
        self.cancion_actual = ruta_archivo
        # stop + unload + small delay to let SDL release resources before loading new file
        pygame.mixer.music.stop()
        if hasattr(pygame.mixer.music, 'unload'):
            pygame.mixer.music.unload()
        time.sleep(0.05)
        try:
            pygame.mixer.music.load(ruta_archivo)
        except pygame.error:
            self.reiniciar_mixer()
            try:
                pygame.mixer.music.load(ruta_archivo)
            except pygame.error:
                return False
        self.posicion_base = 0
        self.en_pausa = False
        self.duracion = duracion
        self.tiempo_inicio_reproduccion = 0
        return True

    def reproducir(self):
        start = 0 if not self.en_pausa else self.posicion_base
        if not self.en_pausa:
            self.posicion_base = 0
        try:
            pygame.mixer.music.play(0, start)
        except pygame.error as e:
            print(f"Play error: {e}")
            return False
        self.en_pausa = False
        self.tiempo_inicio_reproduccion = time.time() - start
        return True

    def pausar(self):
        if self.cancion_actual:
            self.posicion_base = self.obtener_tiempo_actual()
            pygame.mixer.music.pause()
            self.en_pausa = True

    def saltar_a(self, segundos):
        if not self.cancion_actual:
            return False
        self.posicion_base = segundos
        try:
            pygame.mixer.music.play(0, segundos)
        except pygame.error:
            return False
        self.tiempo_inicio_reproduccion = time.time() - segundos
        if self.en_pausa:
            pygame.mixer.music.pause()
        return True

    def obtener_caratula(self):
        try:
            audio = ID3(self.cancion_actual)
            for tag in audio.values():
                if isinstance(tag, APIC):
                    return Image.open(io.BytesIO(tag.data))
        except Exception as e:
            print(f"Album art error: {e}")
        return None

    def obtener_info(self):
        if self.cancion_actual:
            try:
                audio = MP3(self.cancion_actual)
                duracion = audio.info.length
            except Exception as e:
                print(f"Info error: {e}")
                duracion = 0
            try:
                tags = ID3(self.cancion_actual)
                artista = str(tags.get("TPE1", "Artista Desconocido"))
            except:
                artista = "Artista Desconocido"
            return {
                "duracion": duracion,
                "nombre": os.path.basename(self.cancion_actual).replace(".mp3", ""),
                "artista": artista
            }
        return None

    def obtener_tiempo_actual(self):
        if self.en_pausa:
            return self.posicion_base
        try:
            pos = pygame.mixer.music.get_pos()
            if pos > 0:
                return min(self.posicion_base + (pos / 1000.0), self.duracion)
            if pos == -1:
                return self.duracion
        except:
            pass
        if self.tiempo_inicio_reproduccion > 0:
            return min(time.time() - self.tiempo_inicio_reproduccion, self.duracion)
        return 0

    def set_volumen(self, v):
        self.volumen = v
        pygame.mixer.music.set_volume(v)
