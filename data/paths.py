import os
import sys

def get_app_dir():
    """Retorna sys._MEIPASS si está empaquetado, o la raíz del proyecto."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_data_dir():
    """Retorna la carpeta de datos del usuario (no se mezcla con el .exe)."""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    elif sys.platform == 'darwin':
        base = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:
        base = os.environ.get('XDG_DATA_HOME', os.path.join(os.path.expanduser('~'), '.local', 'share'))
    data_dir = os.path.join(base, 'JuanTune')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir
