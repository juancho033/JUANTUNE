import os, threading, hashlib, urllib.request
from data.paths import get_data_dir

CACHE_DIR = os.path.join(get_data_dir(), "cache")
MAX_FILES = 50
MAX_SIZE_MB = 500
_dl_locks = {}

def _ensure():
    os.makedirs(CACHE_DIR, exist_ok=True)

def _path(url):
    return os.path.join(CACHE_DIR, hashlib.md5(url.encode()).hexdigest() + ".mp3")

def _tmp_path(url):
    return _path(url) + ".tmp"

def is_cached(url):
    return os.path.exists(_path(url))

def get_cached_path(url):
    p = _path(url)
    return p if os.path.exists(p) else None

def _validate_mp3(path):
    if not os.path.exists(path):
        return False
    return os.path.getsize(path) > 1000

def download_async(url, on_done=None):
    _ensure()
    dest = _path(url)
    tmp = _tmp_path(url)
    if os.path.exists(dest):
        if on_done:
            on_done(dest)
        return
    if url not in _dl_locks:
        _dl_locks[url] = threading.Lock()
    lock = _dl_locks[url]
    if not lock.acquire(blocking=False):
        return
    def _run():
        try:
            urllib.request.urlretrieve(url, tmp)
            if _validate_mp3(tmp):
                os.replace(tmp, dest)
                _cleanup()
                if on_done:
                    on_done(dest)
            else:
                try:
                    os.remove(tmp)
                except:
                    pass
                if on_done:
                    on_done(None)
        except Exception as e:
            print(f"Download error: {e}")
            try:
                os.remove(tmp)
            except:
                pass
            if on_done:
                on_done(None)
        finally:
            lock.release()
            if url in _dl_locks:
                del _dl_locks[url]
    threading.Thread(target=_run, daemon=True).start()

def download_sync(url):
    _ensure()
    dest = _path(url)
    tmp = _tmp_path(url)
    if os.path.exists(dest):
        return dest
    try:
        urllib.request.urlretrieve(url, tmp)
        if _validate_mp3(tmp):
            os.replace(tmp, dest)
            _cleanup()
            return dest
        else:
            try:
                os.remove(tmp)
            except:
                pass
            return None
    except Exception as e:
        print(f"Download error: {e}")
        try:
            os.remove(tmp)
        except:
            pass
        return None

def _cleanup():
    _ensure()
    try:
        files = sorted(
            (os.path.getmtime(os.path.join(CACHE_DIR, f)), os.path.join(CACHE_DIR, f))
            for f in os.listdir(CACHE_DIR) if f.endswith(".mp3")
        )
        total = sum(os.path.getsize(f) for _, f in files) / (1024*1024)
        while (len(files) > MAX_FILES or total > MAX_SIZE_MB) and files:
            _, path = files.pop(0)
            try:
                s = os.path.getsize(path) / (1024*1024)
                os.remove(path)
                total -= s
            except:
                pass
    except:
        pass
