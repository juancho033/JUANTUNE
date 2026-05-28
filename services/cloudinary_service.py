import json, os, cloudinary, cloudinary.uploader
from data.paths import get_app_dir, get_data_dir

def _find_config(name):
    for d in (get_app_dir(), get_data_dir(), os.getcwd()):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return os.path.join(get_app_dir(), name)

CONFIG_PATH = _find_config("cloudinary_config.json")

def _init():
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    cloudinary.config(cloud_name=cfg["cloud_name"], api_key=cfg["api_key"], api_secret=cfg["api_secret"])

def upload_mp3(file_path, on_progress=None):
    _init()
    result = cloudinary.uploader.upload(file_path, resource_type="video")
    return {"url": result["secure_url"], "public_id": result["public_id"], "duration": result.get("duration", 0)}

def delete_mp3(public_id):
    _init()
    cloudinary.uploader.destroy(public_id, resource_type="video")
