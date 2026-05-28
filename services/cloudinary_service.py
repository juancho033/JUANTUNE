import json, os, cloudinary, cloudinary.uploader

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cloudinary_config.json")

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
