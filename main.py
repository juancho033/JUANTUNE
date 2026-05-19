# main.py
import customtkinter as ctk
import pygame
import random
from config import *
from core.player import ReproductorAudio
from data.database import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import io

class JuanTuneApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("JuanTune")
        self.geometry(f"{ANCHO_APP}x{ALTO_APP}")
        self.configure(fg_color=COLOR_FONDO_PRIMARIO)
        try:
            self.iconbitmap("assets/icons/logo-ico.ico")
        except:
            pass

        self.reproductor = ReproductorAudio()
        self.playlist = [] # Lista de rutas de archivos
        self.indice_actual = 0
        self.duracion_actual = 0
        self.arrastrando_slider = False
        self.shuffle_mode = False
        self.repeat_mode = False
        self.current_playlist_name = None
        self.playlists_data = cargar_playlists()
        self._timer_siguiente = None  # Timer para pasar a siguiente canción
        self._stats_ruta = None
        self._stats_tiempo = 0.0

        # Layout: 3 secciones (sidebar, contenido, barra inferior)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Sidebar izquierdo (fijo)
        self.frame_sidebar = ctk.CTkFrame(self, fg_color=COLOR_FONDO_SECUNDARIO, width=220, corner_radius=0)
        self.frame_sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.frame_sidebar.grid_propagate(False)
        self.crear_sidebar()

        # Main content (centro, scrollable)
        self.frame_main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                                         scrollbar_button_color=COLOR_ACENTO,
                                                         scrollbar_button_hover_color=COLOR_BOTON_HOVER)
        self.frame_main_scroll.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # Home (dashboard - se muestra al iniciar)
        self._en_modo_player = False
        self.frame_home = ctk.CTkFrame(self.frame_main_scroll, fg_color="transparent")
        self.crear_home()
        self.frame_home.pack(fill="both", expand=True)

        # Frame para lista de canciones (se muestra al seleccionar playlist)
        self.frame_lista = ctk.CTkFrame(self.frame_main_scroll, fg_color="transparent")
        self.scroll_playlist = ctk.CTkScrollableFrame(self.frame_lista, fg_color="transparent",
                                                       scrollbar_button_color=COLOR_ACENTO,
                                                       scrollbar_button_hover_color=COLOR_BOTON_HOVER)
        self.scroll_playlist.pack(fill="both", expand=True, padx=30, pady=30)

        # Barra inferior de reproducción (siempre visible)
        self.crear_bottom_bar()

    def crear_home(self):
        """Dashboard de inicio con accesos rápidos y recientes."""
        from data.recent import cargar_recientes

        ctk.CTkLabel(self.frame_home, text="JuanTune", font=(TIPO_FUENTE, 36, "bold"),
                     text_color=COLOR_ACENTO).pack(pady=(30, 5))
        ctk.CTkLabel(self.frame_home, text="Tu reproductor musical", font=(TIPO_FUENTE, 14),
                     text_color=COLOR_TEXTO_SECUNDARIO).pack(pady=(0, 30))

        # Accesos rápidos
        frame_acciones = ctk.CTkFrame(self.frame_home, fg_color="transparent")
        frame_acciones.pack(pady=(0, 30))

        acciones = [
            ("📂", "Abrir Carpeta", self.cargar_carpeta),
            ("🎵", "Elegir Canción", self.cargar_archivo_solo),
            ("📋", "Mis Playlists", self.abrir_selector_playlist),
            ("📊", "Estadísticas", self.abrir_estadisticas),
        ]
        for icono, texto, comando in acciones:
            ctk.CTkButton(frame_acciones, text=f"{icono}  {texto}", font=(TIPO_FUENTE, 15),
                          fg_color=COLOR_FONDO_SECUNDARIO, hover_color=COLOR_ACENTO,
                          width=200, height=50, corner_radius=12,
                          command=comando).pack(side="left", padx=8)

        # Recientes (2 columnas)
        recientes = cargar_recientes()
        if recientes:
            ctk.CTkLabel(self.frame_home, text="Recientes", font=(TIPO_FUENTE, 18, "bold"),
                         text_color=COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(0, 10))

            frame_grid = ctk.CTkScrollableFrame(self.frame_home, fg_color="transparent")
            frame_grid.pack(fill="both", expand=True, padx=20, pady=(0, 10))

            def crear_card_reciente(contenedor, ruta):
                if not os.path.exists(ruta):
                    return
                nombre = os.path.basename(ruta).replace(".mp3", "")
                card = ctk.CTkFrame(contenedor, fg_color=COLOR_FONDO_SECUNDARIO,
                                    corner_radius=12, height=200)
                card.pack(fill="x", padx=5, pady=5)

                frame_img_texto = ctk.CTkFrame(card, fg_color="transparent")
                frame_img_texto.pack(expand=True, fill="both", padx=10, pady=10)

                img_label = ctk.CTkLabel(frame_img_texto, text="🎵", font=("Arial", 30),
                                         width=120, height=120, fg_color=COLOR_FONDO_PRIMARIO,
                                         corner_radius=10)
                img_label.pack(pady=(5, 5))

                try:
                    from core.player import ReproductorAudio
                    r = ReproductorAudio()
                    r.cancion_actual = ruta
                    img = r.obtener_caratula()
                    if img:
                        img.thumbnail((120, 120))
                        img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
                        img_label.configure(image=img_ctk, text="")
                except:
                    pass

                nombre_trunc = (nombre[:20] + '...') if len(nombre) > 20 else nombre
                ctk.CTkLabel(frame_img_texto, text=nombre_trunc, font=(TIPO_FUENTE, 12),
                             wraplength=160).pack(pady=(0, 3))

                card.bind("<Button-1>", lambda e, r=ruta: self.seleccionar_desde_home(r))
                img_label.bind("<Button-1>", lambda e, r=ruta: self.seleccionar_desde_home(r))

            # Agrupar en filas de 2
            for i in range(0, len(recientes), 2):
                fila = ctk.CTkFrame(frame_grid, fg_color="transparent")
                fila.pack(fill="x", pady=2)

                col_izq = ctk.CTkFrame(fila, fg_color="transparent")
                col_izq.pack(side="left", fill="x", expand=True, padx=(0, 5))
                crear_card_reciente(col_izq, recientes[i])

                if i + 1 < len(recientes):
                    col_der = ctk.CTkFrame(fila, fg_color="transparent")
                    col_der.pack(side="left", fill="x", expand=True, padx=(5, 0))
                    crear_card_reciente(col_der, recientes[i + 1])

    def crear_sidebar(self):
        """Barra lateral de navegación (estilo Spotify)."""
        ctk.CTkLabel(self.frame_sidebar, text="JuanTune", font=(TIPO_FUENTE, 22, "bold"),
                     text_color=COLOR_ACENTO).pack(pady=(25, 20))

        frame_nav = ctk.CTkFrame(self.frame_sidebar, fg_color="transparent")
        frame_nav.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkButton(frame_nav, text="🏠  Inicio", anchor="w", font=(TIPO_FUENTE, 14),
                      fg_color="transparent", hover_color=COLOR_FONDO_PRIMARIO,
                      command=lambda: self.mostrar_vista("home")).pack(fill="x", pady=1)

        ctk.CTkButton(frame_nav, text="📚  Biblioteca", anchor="w", font=(TIPO_FUENTE, 14),
                      fg_color="transparent", hover_color=COLOR_FONDO_PRIMARIO,
                      command=lambda: self.mostrar_vista("biblioteca")).pack(fill="x", pady=1)

        ctk.CTkFrame(self.frame_sidebar, height=1, fg_color=COLOR_FONDO_PRIMARIO).pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(self.frame_sidebar, text="TUS PLAY LISTS", font=(TIPO_FUENTE, 11, "bold"),
                     text_color=COLOR_TEXTO_SECUNDARIO).pack(anchor="w", padx=12, pady=(0, 5))

        ctk.CTkButton(self.frame_sidebar, text="+  Crear Playlist", anchor="w",
                      font=(TIPO_FUENTE, 13), fg_color="transparent",
                      hover_color=COLOR_FONDO_PRIMARIO,
                      command=self.abrir_popup_crear_playlist).pack(fill="x", padx=12, pady=2)

        self.scroll_playlists_sidebar = ctk.CTkScrollableFrame(self.frame_sidebar, fg_color="transparent")
        self.scroll_playlists_sidebar.pack(fill="both", expand=True, padx=12, pady=2)
        self._actualizar_sidebar_playlists()

        frame_gestion = ctk.CTkFrame(self.frame_sidebar, fg_color="transparent")
        frame_gestion.pack(side="bottom", fill="x", padx=12, pady=(5, 15))

        self.btn_salir_playlist = ctk.CTkButton(frame_gestion, text="✕ Cerrar Playlist",
                                                  fg_color="transparent",
                                                  hover_color=COLOR_FONDO_PRIMARIO,
                                                  font=(TIPO_FUENTE, 12),
                                                  command=self.salir_playlist)
        self.btn_salir_playlist.pack(fill="x", pady=1)
        self.btn_salir_playlist.configure(state="disabled")

        ctk.CTkButton(frame_gestion, text="🗑 Eliminar Playlist", fg_color="transparent",
                       hover_color=COLOR_FONDO_PRIMARIO, text_color="#FF5555",
                       font=(TIPO_FUENTE, 12),
                       command=self.eliminar_playlist_actual).pack(fill="x", pady=1)

    def _actualizar_sidebar_playlists(self):
        """Refresca la lista de playlists en la sidebar."""
        for widget in self.scroll_playlists_sidebar.winfo_children():
            widget.destroy()
        nombres = [p["name"] for p in self.playlists_data["playlists"]]
        for nombre in nombres:
            btn = ctk.CTkButton(self.scroll_playlists_sidebar, text=nombre, anchor="w",
                                font=(TIPO_FUENTE, 13), fg_color="transparent",
                                hover_color=COLOR_FONDO_PRIMARIO,
                                command=lambda n=nombre: self.seleccionar_playlist(n))
            btn.pack(fill="x", pady=1)

    def crear_bottom_bar(self):
        """Barra inferior de reproducción (estilo Spotify)."""
        self.frame_bottom = ctk.CTkFrame(self, fg_color=COLOR_FONDO_SECUNDARIO, height=80, corner_radius=0)
        self.frame_bottom.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.frame_bottom.grid_propagate(False)

        self.frame_bottom.grid_columnconfigure(0, weight=1)
        self.frame_bottom.grid_columnconfigure(1, weight=2)
        self.frame_bottom.grid_columnconfigure(2, weight=1)

        # LEFT: Mini album art + title
        frame_left = ctk.CTkFrame(self.frame_bottom, fg_color="transparent")
        frame_left.grid(row=0, column=0, sticky="w", padx=15)

        self.img_caratula = ctk.CTkLabel(frame_left, text="🎵", font=("Arial", 20),
                                         width=56, height=56, fg_color=COLOR_FONDO_PRIMARIO,
                                         corner_radius=6)
        self.img_caratula.pack(side="left", padx=(0, 10))

        frame_info = ctk.CTkFrame(frame_left, fg_color="transparent")
        frame_info.pack(side="left")

        self.lbl_titulo = ctk.CTkLabel(frame_info, text="", font=(TIPO_FUENTE, 13, "bold"),
                                       anchor="w")
        self.lbl_titulo.pack(anchor="w")

        self.lbl_subtitulo = ctk.CTkLabel(frame_info, text="Sin reproducción", font=(TIPO_FUENTE, 11),
                                          text_color=COLOR_TEXTO_SECUNDARIO, anchor="w")
        self.lbl_subtitulo.pack(anchor="w")

        # CENTER: Controls + progress
        frame_center = ctk.CTkFrame(self.frame_bottom, fg_color="transparent")
        frame_center.grid(row=0, column=1, sticky="nsew")

        frame_btns = ctk.CTkFrame(frame_center, fg_color="transparent")
        frame_btns.pack(pady=(6, 2))

        self.btn_shuffle = ctk.CTkButton(frame_btns, text="🔀", width=30, height=30, corner_radius=15,
                                          fg_color="transparent", hover=False, font=("Arial", 12),
                                          command=self.toggle_shuffle)
        self.btn_shuffle.pack(side="left", padx=4)

        ctk.CTkButton(frame_btns, text="⏮", width=32, height=32, corner_radius=16,
                      fg_color="transparent", hover=False, font=("Arial", 14),
                      command=self.anterior_cancion).pack(side="left", padx=4)

        self.btn_play = ctk.CTkButton(frame_btns, text="▶", width=40, height=40, corner_radius=20,
                                       fg_color=COLOR_ACENTO, hover_color=COLOR_BOTON_HOVER,
                                       font=("Arial", 18), command=self.click_play)
        self.btn_play.pack(side="left", padx=8)

        ctk.CTkButton(frame_btns, text="⏭", width=32, height=32, corner_radius=16,
                      fg_color="transparent", hover=False, font=("Arial", 14),
                      command=self.siguiente_cancion).pack(side="left", padx=4)

        self.btn_repeat = ctk.CTkButton(frame_btns, text="🔁", width=30, height=30, corner_radius=15,
                                         fg_color="transparent", hover=False, font=("Arial", 12),
                                         command=self.toggle_repeat)
        self.btn_repeat.pack(side="left", padx=4)

        frame_progress = ctk.CTkFrame(frame_center, fg_color="transparent")
        frame_progress.pack(fill="x", padx=30, pady=(0, 2))

        self.lbl_tiempo_actual = ctk.CTkLabel(frame_progress, text="0:00", font=(TIPO_FUENTE, 10),
                                               text_color=COLOR_TEXTO_SECUNDARIO, width=35)
        self.lbl_tiempo_actual.pack(side="left")

        self.slider_progreso = ctk.CTkSlider(frame_progress, from_=0, to=100, height=6,
                                               button_length=18, button_corner_radius=9,
                                               button_color=COLOR_ACENTO, progress_color=COLOR_ACENTO,
                                               button_hover_color=COLOR_BOTON_HOVER, hover=False)
        self.slider_progreso.pack(side="left", fill="x", expand=True, padx=5)
        self.slider_progreso.set(0)
        self.slider_progreso.bind("<ButtonPress-1>", self.slider_press)
        self.slider_progreso.bind("<ButtonRelease-1>", self.slider_release)

        self.lbl_tiempo_total = ctk.CTkLabel(frame_progress, text="0:00", font=(TIPO_FUENTE, 10),
                                              text_color=COLOR_TEXTO_SECUNDARIO, width=35)
        self.lbl_tiempo_total.pack(side="left")

        # RIGHT: Volume
        frame_right = ctk.CTkFrame(self.frame_bottom, fg_color="transparent")
        frame_right.grid(row=0, column=2, sticky="e", padx=15)

        ctk.CTkLabel(frame_right, text="🔊", font=("Arial", 12)).pack(side="left", padx=(0, 5))

        self.slider_volumen = ctk.CTkSlider(frame_right, from_=0, to=100, height=4,
                                             button_color=COLOR_ACENTO, progress_color=COLOR_ACENTO,
                                             button_hover_color=COLOR_BOTON_HOVER,
                                             command=self.cambiar_volumen, width=100)
        self.slider_volumen.pack(side="left")
        self.slider_volumen.set(50)

        self.lbl_volumen = ctk.CTkLabel(frame_right, text="50%", font=(TIPO_FUENTE, 11),
                                         text_color=COLOR_TEXTO_SECUNDARIO, width=30)
        self.lbl_volumen.pack(side="left", padx=(5, 0))

    def crear_panel_playlist(self):
        """Configura la vista de playlist en el área principal."""
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        # Header con nombre de playlist
        frame_header = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        frame_header.pack(fill="x", padx=30, pady=(30, 10))

        lbl = ctk.CTkLabel(frame_header, text=self.current_playlist_name or "Playlist",
                           font=(TIPO_FUENTE, 24, "bold"), text_color=COLOR_ACENTO)
        lbl.pack(side="left")

        btn_back = ctk.CTkButton(frame_header, text="← Volver", fg_color="transparent",
                                 hover_color=COLOR_FONDO_SECUNDARIO, font=(TIPO_FUENTE, 13),
                                 command=self.salir_playlist, width=80)
        btn_back.pack(side="right", padx=(0, 5))

        btn_del = ctk.CTkButton(frame_header, text="Eliminar", fg_color="transparent",
                                hover_color=COLOR_FONDO_SECUNDARIO, text_color="#FF5555",
                                font=(TIPO_FUENTE, 13), command=self.eliminar_playlist_actual)
        btn_del.pack(side="right", padx=(0, 5))

        # Acciones
        frame_acc = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
        frame_acc.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkButton(frame_acc, text="+ Añadir Carpeta", fg_color="transparent",
                      hover_color=COLOR_FONDO_SECUNDARIO, font=(TIPO_FUENTE, 13),
                      command=self.cargar_carpeta).pack(side="left", padx=(0, 8))

        ctk.CTkButton(frame_acc, text="+ Añadir Canción", fg_color="transparent",
                      hover_color=COLOR_FONDO_SECUNDARIO, font=(TIPO_FUENTE, 13),
                      command=self.cargar_archivo_solo).pack(side="left")

        # Lista de canciones
        self.scroll_playlist = ctk.CTkScrollableFrame(self.frame_lista, fg_color="transparent",
                                                       scrollbar_button_color=COLOR_ACENTO,
                                                       scrollbar_button_hover_color=COLOR_BOTON_HOVER)
        self.scroll_playlist.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        if self.current_playlist_name:
            self.cargar_playlist_a_ui(self.current_playlist_name)

    def cargar_carpeta(self):
        directorio = filedialog.askdirectory()
        if directorio:
            primeras = []
            for archivo in os.listdir(directorio):
                if archivo.lower().endswith(".mp3"):
                    ruta_completa = os.path.join(directorio, archivo)
                    if ruta_completa not in self.playlist:
                        self.playlist.append(ruta_completa)
                        self.añadir_a_playlist_ui(ruta_completa)
                        if self.current_playlist_name:
                            añadir_cancion_playlist(self.current_playlist_name, ruta_completa)
                        if not primeras:
                            primeras.append(ruta_completa)
            if primeras and not self.reproductor.cancion_actual:
                self.seleccionar_cancion(primeras[0])

    def _obtener_mini_caratula(self, ruta, size=32):
        """Retorna un CTkImage con la carátula o None."""
        try:
            from mutagen.id3 import ID3, APIC
            audio = ID3(ruta)
            for tag in audio.values():
                if isinstance(tag, APIC):
                    img = Image.open(io.BytesIO(tag.data))
                    img.thumbnail((size, size))
                    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        except:
            pass
        return None

    def añadir_a_playlist_ui(self, ruta):
        nombre = os.path.basename(ruta).replace(".mp3", "")
        nombre_truncado = (nombre[:35] + '...') if len(nombre) > 35 else nombre
        frame_song = ctk.CTkFrame(self.scroll_playlist, fg_color="transparent")
        frame_song.pack(fill="x", pady=1)

        # Mini carátula
        img_ctk = self._obtener_mini_caratula(ruta)
        lbl_img = ctk.CTkLabel(frame_song, text="🎵" if not img_ctk else "",
                               image=img_ctk, font=("Arial", 16),
                               width=36, height=36, fg_color=COLOR_FONDO_PRIMARIO, corner_radius=4)
        lbl_img.pack(side="left", padx=(4, 8))

        # Botón de canción
        btn_song = ctk.CTkButton(frame_song, text=nombre_truncado, anchor="w",
                                 fg_color="transparent", hover_color=COLOR_FONDO_PRIMARIO,
                                 font=(TIPO_FUENTE, 13),
                                 command=lambda r=ruta: self.seleccionar_cancion(r))
        btn_song.pack(side="left", fill="x", expand=True, ipady=6)

        # Botón eliminar (solo si hay una playlist con nombre)
        if self.current_playlist_name:
            btn_remove = ctk.CTkButton(frame_song, text="✕", width=28,
                                       fg_color="transparent", hover_color=COLOR_FONDO_PRIMARIO,
                                       font=(TIPO_FUENTE, 12), text_color="#FF5555",
                                       command=lambda r=ruta: self.eliminar_cancion_de_playlist(r))
            btn_remove.pack(side="right", padx=(4, 4))

    def seleccionar_cancion(self, ruta):
        # Guardar tiempo acumulado de la canción anterior
        self._flush_stats()

        if ruta in self.playlist:
            self.indice_actual = self.playlist.index(ruta)
        if self.reproductor.cargar_cancion(ruta):
            info = self.reproductor.obtener_info()
            self.lbl_titulo.configure(text=(info['nombre'][:35] + '...') if len(info['nombre']) > 35 else info['nombre'])
            self.duracion_actual = info['duracion']
            self.slider_progreso.configure(to=info['duracion'])
            self.slider_progreso.set(0)

            img = self.reproductor.obtener_caratula()
            if img:
                img.thumbnail((56, 56))
                img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(56, 56))
                self.img_caratula.configure(image=img_ctk, text="")
            else:
                self.img_caratula.configure(image=None, text="🎵")

            # Empezar a trackear la nueva canción
            self._stats_ruta = ruta
            self._stats_tiempo = 0.0

            self.reproductor.reproducir()
            self.btn_play.configure(text="⏸")
            self._en_modo_player = True
            self.actualizar_barra_tiempo()
            from data.recent import añadir_reciente
            añadir_reciente(ruta)

    def mostrar_vista(self, vista):
        """Cambia entre vistas del contenido principal: 'home' o 'biblioteca'."""
        if vista == "home":
            self.frame_lista.pack_forget()
            self.frame_home.pack(fill="both", expand=True)
        else:
            self.frame_home.pack_forget()
            if not self.current_playlist_name:
                self.crear_biblioteca()
            self.frame_lista.pack(fill="both", expand=True)

    def crear_biblioteca(self):
        """Vista de biblioteca con tarjetas de playlists."""
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        ctk.CTkLabel(self.frame_lista, text="Tu Biblioteca", font=(TIPO_FUENTE, 26, "bold"),
                     text_color=COLOR_ACENTO).pack(pady=(30, 20))

        nombres = [p["name"] for p in self.playlists_data["playlists"]]
        if not nombres:
            ctk.CTkLabel(self.frame_lista, text="No tienes playlists aún.\nCrea una desde la barra lateral.",
                         font=(TIPO_FUENTE, 14), text_color=COLOR_TEXTO_SECUNDARIO,
                         justify="center").pack(expand=True)
            return

        scroll = ctk.CTkScrollableFrame(self.frame_lista, fg_color="transparent",
                                         scrollbar_button_color=COLOR_ACENTO,
                                         scrollbar_button_hover_color=COLOR_BOTON_HOVER)
        scroll.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        fila = None
        for i, nombre in enumerate(nombres):
            if i % 2 == 0:
                fila = ctk.CTkFrame(scroll, fg_color="transparent")
                fila.pack(fill="x", pady=4)
            card = ctk.CTkFrame(fila, fg_color=COLOR_FONDO_SECUNDARIO, corner_radius=12, height=100)
            card.pack(side="left", fill="x", expand=True, padx=4)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text="📋", font=("Arial", 28)).pack(pady=(12, 2))
            ctk.CTkLabel(card, text=nombre, font=(TIPO_FUENTE, 14, "bold"),
                         text_color=COLOR_TEXTO_PRINCIPAL).pack()
            canciones = obtener_canciones_playlist(nombre)
            ctk.CTkLabel(card, text=f"{len(canciones)} canciones",
                         font=(TIPO_FUENTE, 11), text_color=COLOR_TEXTO_SECUNDARIO).pack()
            card.bind("<Button-1>", lambda e, n=nombre: self.seleccionar_playlist(n))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, n=nombre: self.seleccionar_playlist(n))

    def volver_al_inicio(self):
        """Detiene reproducción y regresa al dashboard."""
        self._flush_stats()
        self._stats_ruta = None
        if self.reproductor.cancion_actual:
            self.reproductor.pausar()
            self.btn_play.configure(text="▶")
        self.mostrar_vista("home")
        self.lbl_subtitulo.configure(text="Sin reproducción")

    def seleccionar_desde_home(self, ruta):
        """Selecciona canción desde una tarjeta del dashboard."""
        self.seleccionar_cancion(ruta)

    def abrir_selector_playlist(self):
        """Abre popup para seleccionar una playlist."""
        nombres = [p["name"] for p in self.playlists_data["playlists"]]
        if not nombres:
            messagebox.showinfo("Sin playlists", "Crea una playlist primero")
            return
        top = ctk.CTkToplevel(self)
        top.title("Seleccionar Playlist")
        top.geometry("300x280")
        top.configure(fg_color=COLOR_FONDO_PRIMARIO)
        top.transient(self)
        top.grab_set()
        ctk.CTkLabel(top, text="Elige una playlist:", font=(TIPO_FUENTE, 16, "bold"),
                     text_color=COLOR_ACENTO).pack(pady=20)
        for nombre in nombres:
            ctk.CTkButton(top, text=nombre, fg_color=COLOR_FONDO_SECUNDARIO,
                          hover_color=COLOR_ACENTO,
                          command=lambda n=nombre: [self.seleccionar_playlist(n), top.destroy()]
                          ).pack(fill="x", padx=20, pady=4)
        ctk.CTkButton(top, text="Cancelar", fg_color="transparent",
                      command=top.destroy).pack(pady=(20, 10))

    def abrir_estadisticas(self):
        """Ventana de estadísticas de reproducción."""
        from data.stats import cargar_stats, obtener_top, total_plays, total_time, unique_songs

        win = ctk.CTkToplevel(self)
        win.title("Estadísticas")
        win.geometry("700x720")
        win.configure(fg_color=COLOR_FONDO_PRIMARIO)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text="Estadísticas", font=(TIPO_FUENTE, 26, "bold"),
                     text_color=COLOR_ACENTO).pack(pady=(25, 20))

        # Resumen
        frame_resumen = ctk.CTkFrame(win, fg_color=COLOR_FONDO_SECUNDARIO, corner_radius=15)
        frame_resumen.pack(fill="x", padx=30, pady=(0, 20))

        total_seg = total_time()
        horas = int(total_seg // 3600)
        minutos = int((total_seg % 3600) // 60)

        datos = [
            ("🎵 Canciones distintas", str(unique_songs())),
            ("▶️ Reproducciones totales", str(total_plays())),
            ("⏱️ Tiempo escuchado", f"{horas}h {minutos}m"),
        ]
        for label, valor in datos:
            row = ctk.CTkFrame(frame_resumen, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)
            ctk.CTkLabel(row, text=label, font=(TIPO_FUENTE, 14),
                         text_color=COLOR_TEXTO_SECUNDARIO).pack(side="left")
            ctk.CTkLabel(row, text=valor, font=(TIPO_FUENTE, 16, "bold"),
                         text_color=COLOR_TEXTO_PRINCIPAL).pack(side="right")

        # Top canciones
        ctk.CTkLabel(win, text="Más reproducidas", font=(TIPO_FUENTE, 18, "bold"),
                     text_color=COLOR_TEXTO_PRINCIPAL).pack(anchor="w", padx=30, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent",
                                         scrollbar_button_color=COLOR_ACENTO,
                                         scrollbar_button_hover_color=COLOR_BOTON_HOVER)
        scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        top = obtener_top(15)
        if not top:
            ctk.CTkLabel(scroll, text="Aún no hay datos\nReproduce algunas canciones para ver estadísticas",
                         font=(TIPO_FUENTE, 14), text_color=COLOR_TEXTO_SECUNDARIO,
                         justify="center").pack(expand=True, pady=40)
        else:
            for i, (ruta, datos_cancion) in enumerate(top, 1):
                nombre = os.path.basename(ruta).replace(".mp3", "")
                nombre = (nombre[:40] + '...') if len(nombre) > 40 else nombre

                row = ctk.CTkFrame(scroll, fg_color=COLOR_FONDO_SECUNDARIO, corner_radius=10)
                row.pack(fill="x", pady=3)

                ctk.CTkLabel(row, text=f"#{i}", font=(TIPO_FUENTE, 14, "bold"),
                             text_color=COLOR_ACENTO, width=40).pack(side="left", padx=(10, 5))

                ctk.CTkLabel(row, text=nombre, font=(TIPO_FUENTE, 13),
                             anchor="w").pack(side="left", fill="x", expand=True, padx=(5, 10))

                plays_text = f"{datos_cancion['plays']} {'vez' if datos_cancion['plays'] == 1 else 'veces'}"
                ctk.CTkLabel(row, text=plays_text, font=(TIPO_FUENTE, 13),
                             text_color=COLOR_TEXTO_SECUNDARIO).pack(side="right", padx=(0, 15))

                row.bind("<Button-1>", lambda e, r=ruta: [win.destroy(), self.seleccionar_cancion(r)])
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, r=ruta: [win.destroy(), self.seleccionar_cancion(r)])

        ctk.CTkButton(win, text="Cerrar", command=win.destroy,
                      fg_color="transparent", border_width=1).pack(pady=(0, 20))

    def _programar_timer_siguiente(self):
        """Cancela timer anterior y programa siguiente canción basado en tiempo restante."""
        pass  # Ya no se usa, detection se hace en actualizar_barra_tiempo

    def slider_press(self, event=None):
        """Marca cuando el usuario empieza a arrastrar el slider."""
        self.arrastrando_slider = True

    def slider_release(self, event=None):
        """Salta a la posición seleccionada en el slider."""
        self.arrastrando_slider = False
        valor = self.slider_progreso.get()
        if self.reproductor.cancion_actual:
            self.reproductor.saltar_a(valor)
            # Actualizar inmediatamente la UI
            self.actualizar_barra_tiempo()

    def _flush_stats(self):
        """Guarda el tiempo acumulado de la canción actual en estadísticas."""
        if self._stats_ruta and self._stats_tiempo > 0:
            from data.stats import registrar_reproduccion
            registrar_reproduccion(self._stats_ruta, self._stats_tiempo)
        self._stats_tiempo = 0.0

    def _formatear_tiempo(self, segundos):
        segundos = int(segundos)
        m = segundos // 60
        s = segundos % 60
        return f"{m}:{s:02d}"

    def actualizar_barra_tiempo(self):
        """Actualiza la barra de progreso y detecta fin de canción."""
        if not self._en_modo_player:
            return
        if self.reproductor.cancion_actual and not self.arrastrando_slider:
            tiempo = self.reproductor.obtener_tiempo_actual()
            self.slider_progreso.set(tiempo)
            self.lbl_tiempo_actual.configure(text=self._formatear_tiempo(tiempo))
            self.lbl_tiempo_total.configure(text=self._formatear_tiempo(self.duracion_actual))

            if not self.reproductor.en_pausa and self._stats_ruta:
                self._stats_tiempo += 0.5
            
            if tiempo >= self.duracion_actual - 0.2:
                self._flush_stats()
                self.siguiente_cancion()
        
        self.after(500, self.actualizar_barra_tiempo)

    def cambiar_volumen(self, valor):
        """Ajusta el volumen del reproductor."""
        volumen = float(valor) / 100.0
        self.reproductor.set_volumen(volumen)
        self.lbl_volumen.configure(text=f"{int(valor)}%")

    def toggle_shuffle(self):
        """Alterna el modo de reproducción aleatoria."""
        self.shuffle_mode = not self.shuffle_mode
        if self.shuffle_mode:
            self.btn_shuffle.configure(fg_color=COLOR_ACENTO)
        else:
            self.btn_shuffle.configure(fg_color="transparent")

    def toggle_repeat(self):
        """Alterna el modo de repetición de canción."""
        self.repeat_mode = not self.repeat_mode
        if self.repeat_mode:
            self.btn_repeat.configure(fg_color=COLOR_ACENTO)
        else:
            self.btn_repeat.configure(fg_color="transparent")

    def click_play(self):
        """Toggle entre play y pause."""
        if not self.reproductor.cancion_actual:
            return
        if self.reproductor.en_pausa:
            self.reproductor.reproducir()
            self.btn_play.configure(text="⏸")
        else:
            self.reproductor.pausar()
            self.btn_play.configure(text="▶")

    def cargar_archivo_solo(self):
        """Añade una sola canción a la lista."""
        ruta = filedialog.askopenfilename(filetypes=[("MP3", "*.mp3")])
        if ruta:
            if ruta not in self.playlist:
                self.playlist.append(ruta)
                self.añadir_a_playlist_ui(ruta)
                if self.current_playlist_name:
                    añadir_cancion_playlist(self.current_playlist_name, ruta)
            self.seleccionar_cancion(ruta)

    def siguiente_cancion(self):
        """Salta a la siguiente canción, repite la actual o elige aleatoria."""
        if len(self.playlist) > 0:
            if self.repeat_mode:
                # Repetir la misma canción
                self.seleccionar_cancion(self.playlist[self.indice_actual])
            elif self.shuffle_mode:
                self.indice_actual = random.randint(0, len(self.playlist) - 1)
                nueva_ruta = self.playlist[self.indice_actual]
                self.seleccionar_cancion(nueva_ruta)
            else:
                self.indice_actual = (self.indice_actual + 1) % len(self.playlist)
                nueva_ruta = self.playlist[self.indice_actual]
                self.seleccionar_cancion(nueva_ruta)

    def salir_playlist(self):
        """Sale del modo playlist y vuelve a la biblioteca."""
        self.current_playlist_name = None
        self.playlist = []
        self.btn_salir_playlist.configure(state="disabled")
        self.mostrar_vista("biblioteca")

    def abrir_popup_crear_playlist(self):
        """Abre un popup para crear una nueva playlist con sus canciones."""
        popup = ctk.CTkToplevel(self)
        popup.title("Nueva Playlist")
        popup.geometry("600x650")
        popup.configure(fg_color=COLOR_FONDO_PRIMARIO)
        popup.transient(self)
        popup.grab_set()

        ctk.CTkLabel(popup, text="Crear Playlist", font=(TIPO_FUENTE, 22, "bold"),
                     text_color=COLOR_ACENTO).pack(pady=(20, 15))

        frame = ctk.CTkFrame(popup, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(frame, text="Nombre de la playlist:", font=(TIPO_FUENTE, 14)).pack(anchor="w")
        entry_nombre = ctk.CTkEntry(frame, placeholder_text="Ej: Mis favoritas")
        entry_nombre.pack(fill="x", pady=(5, 15))

        ctk.CTkLabel(frame, text="Canciones:", font=(TIPO_FUENTE, 14)).pack(anchor="w")

        canciones_seleccionadas = []

        scroll_canciones = ctk.CTkScrollableFrame(frame, height=180, fg_color=COLOR_FONDO_SECUNDARIO)
        scroll_canciones.pack(fill="x", pady=(10, 15))

        def actualizar_lista_canciones():
            for widget in scroll_canciones.winfo_children():
                widget.destroy()
            for i, ruta in enumerate(canciones_seleccionadas):
                nombre = os.path.basename(ruta).replace(".mp3", "")
                frame_item = ctk.CTkFrame(scroll_canciones, fg_color="transparent")
                frame_item.pack(fill="x", pady=2)
                ctk.CTkLabel(frame_item, text=nombre, anchor="w").pack(side="left", fill="x", expand=True)
                btn_eliminar = ctk.CTkButton(frame_item, text="✕", width=30, fg_color="transparent",
                                              command=lambda r=ruta: (canciones_seleccionadas.remove(r), actualizar_lista_canciones()))
                btn_eliminar.pack(side="right")

        def añadir_canciones_popup():
            rutas = filedialog.askopenfilenames(filetypes=[("MP3", "*.mp3")])
            for ruta in rutas:
                if ruta not in canciones_seleccionadas:
                    canciones_seleccionadas.append(ruta)
            actualizar_lista_canciones()

        frame_btn_canciones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_btn_canciones.pack(fill="x", pady=(0, 15))
        ctk.CTkButton(frame_btn_canciones, text="+ Añadir Canciones", command=añadir_canciones_popup,
                      fg_color="transparent", border_width=1, border_color=COLOR_ACENTO
                      ).pack(side="left", fill="x", expand=True)

        def crear_desde_popup():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Error", "Ingresa un nombre para la playlist")
                return
            if nombre in [p["name"] for p in self.playlists_data["playlists"]]:
                messagebox.showwarning("Error", "Ya existe una playlist con ese nombre")
                return
            crear_playlist(nombre)
            for ruta in canciones_seleccionadas:
                añadir_cancion_playlist(nombre, ruta)
            self.playlists_data = cargar_playlists()
            self._actualizar_sidebar_playlists()
            popup.destroy()
            self.seleccionar_playlist(nombre)

        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(fill="x")
        ctk.CTkButton(frame_botones, text="Cancelar", fg_color="transparent", border_width=1,
                      command=popup.destroy).pack(side="left", padx=(0, 10), fill="x", expand=True)
        ctk.CTkButton(frame_botones, text="Crear Playlist", fg_color=COLOR_ACENTO,
                      command=crear_desde_popup).pack(side="left", fill="x", expand=True)

    def seleccionar_playlist(self, nombre):
        self.current_playlist_name = nombre
        self.btn_salir_playlist.configure(state="normal")
        self.crear_panel_playlist()
        self.mostrar_vista("biblioteca")

    def cargar_playlist_a_ui(self, nombre):
        """Carga las canciones de una playlist a la UI."""
        self.playlist = []
        self.limpiar_ui_playlist()
        canciones = obtener_canciones_playlist(nombre)
        for ruta in canciones:
            if os.path.exists(ruta):  # Solo añadir si el archivo existe
                self.playlist.append(ruta)
                self.añadir_a_playlist_ui(ruta)

    def eliminar_cancion_de_playlist(self, ruta):
        """Elimina una canción de la playlist actual y de la UI."""
        if self.current_playlist_name:
            from data.database import eliminar_cancion_playlist
            eliminar_cancion_playlist(self.current_playlist_name, ruta)
            if ruta in self.playlist:
                self.playlist.remove(ruta)
            self.cargar_playlist_a_ui(self.current_playlist_name)

    def limpiar_ui_playlist(self):
        """Elimina todos los botones de canciones en la UI."""
        for widget in self.scroll_playlist.winfo_children():
            widget.destroy()

    def eliminar_playlist_actual(self):
        """Elimina la playlist actual."""
        if self.current_playlist_name:
            if messagebox.askyesno("Confirmar", f"¿Eliminar la playlist '{self.current_playlist_name}'?"):
                eliminar_playlist(self.current_playlist_name)
                self.playlists_data = cargar_playlists()
                self._actualizar_sidebar_playlists()
                self.salir_playlist()






    def anterior_cancion(self):
        """Salta a la canción anterior en la lista."""
        if len(self.playlist) > 0:
            self.indice_actual = (self.indice_actual - 1) % len(self.playlist)
            nueva_ruta = self.playlist[self.indice_actual]
            self.seleccionar_cancion(nueva_ruta)

if __name__ == "__main__":
    app = JuanTuneApp()
    app.mainloop()