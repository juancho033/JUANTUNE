import json, os, time
from data.paths import get_data_dir

CLOUD_CACHE_FILE = os.path.join(get_data_dir(), "cloud_cache.json")
CACHE_DURATION = 1800

def load_cloud_cache():
    if os.path.exists(CLOUD_CACHE_FILE):
        try:
            with open(CLOUD_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return None

def save_cloud_cache(songs):
    data = {"timestamp": time.time(), "songs": songs}
    with open(CLOUD_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_cache_valid():
    data = load_cloud_cache()
    return data and ("timestamp" in data) and (time.time() - data["timestamp"] < CACHE_DURATION)

def get_cached_songs():
    data = load_cloud_cache()
    return data.get("songs", []) if data else []
