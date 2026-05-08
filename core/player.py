# core/player.py
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
        # tiempo_inicio_reproduccion: momento exacto (time.time()) en que inició la sesión actual
        # (ya sea play normal o después de un seek)
        self.tiempo_inicio_reproduccion = 0
        pygame.mixer.music.set_volume(self.volumen)

    def cargar_cancion(self, ruta_archivo):
        if os.path.exists(ruta_archivo):
            pygame.mixer.music.stop()
            self.cancion_actual = ruta_archivo
            pygame.mixer.music.load(ruta_archivo)
            self.posicion_base = 0
            self.en_pausa = False
            # Obtener duración
            audio = MP3(ruta_archivo)
            self.duracion = audio.info.length
            # Iniciar tiempo
            self.tiempo_inicio_reproduccion = time.time()
            return True
        return False

    def reproducir(self):
        if self.en_pausa:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play()
        self.en_pausa = False
        # Actualizar tiempo de inicio
        self.tiempo_inicio_reproduccion = time.time()

    def pausar(self):
        pygame.mixer.music.pause()
        self.en_pausa = True

    def saltar_a(self, segundos):
        """Mueve la reproducción al segundo indicado."""
        if self.cancion_actual:
            self.posicion_base = segundos
            pygame.mixer.music.play(0, segundos)
            # CRÍTICO: tiempo_inicio_reproduccion debe ser AHORA MENOS los segundos
            # Para que obtener_tiempo_actual() = segundos + (tiempo_actual - (ahora - segundos))
            self.tiempo_inicio_reproduccion = time.time() - segundos
            if self.en_pausa:
                pygame.mixer.music.pause()
            return True
        return False

    def obtener_caratula(self):
        """Extrae la imagen del MP3. Retorna un objeto PIL Image o None."""
        try:
            audio = ID3(self.cancion_actual)
            for tag in audio.values():
                if isinstance(tag, APIC):
                    return Image.open(io.BytesIO(tag.data))
        except:
            pass
        return None

    def obtener_info(self):
        if self.cancion_actual:
            audio = MP3(self.cancion_actual)
            return {
                "duracion": audio.info.length,
                "nombre": os.path.basename(self.cancion_actual).replace(".mp3", "")
            }
        return None

    def obtener_tiempo_actual(self):
        """Obtiene el tiempo actual usando pygame.get_pos() (más confiable)."""
        if self.en_pausa:
            return self.posicion_base
        
        # Usar get_pos() como fuente principal (devuelve milisegundos)
        pos = pygame.mixer.music.get_pos()
        if pos > 0:
            # get_pos() devuelve el tiempo desde que se inició el play actual
            return min(self.posicion_base + (pos / 1000.0), self.duracion)
        
        # Si get_pos() es -1, la canción terminó
        if pos == -1:
            return self.duracion
            
        # Respaldo: usar tiempo del sistema (tiempo_inicio ya compensa posicion_base)
        return min(time.time() - self.tiempo_inicio_reproduccion, self.duracion)

    def set_volumen(self, v):
        self.volumen = v
        pygame.mixer.music.set_volume(v)
