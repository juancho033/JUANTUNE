import json, os
import urllib.request
import urllib.error
import urllib.parse
from data.paths import get_app_dir, get_data_dir

def _find_config(name):
    for d in (get_app_dir(), get_data_dir(), os.getcwd()):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return os.path.join(get_app_dir(), name)

def _load_config():
    cfg = _find_config("firebase_config.json")
    with open(cfg) as f:
        return json.load(f)

_config = _load_config()
PROJECT = _config.get("project_id", "juantune")
API_KEY = _config["api_key"]
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/%28default%29/documents"

def _url(base, **params):
    qs = urllib.parse.urlencode(params)
    return f"{base}?{qs}"

def _make_doc(d):
    fields = d.get("fields", {})
    out = {"id": d["name"].split("/")[-1]}
    for key, val in fields.items():
        for v in val.values():
            out[key] = v
            break
    return out

def _to_fields(data):
    fields = {}
    for key, val in data.items():
        if val is None:
            continue
        if isinstance(val, bool):
            fields[key] = {"booleanValue": val}
        elif isinstance(val, int):
            fields[key] = {"integerValue": str(val)}
        elif isinstance(val, float):
            fields[key] = {"doubleValue": val}
        else:
            fields[key] = {"stringValue": str(val)}
    return fields

def _request(method, url, body=None):
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        if resp.status == 204:
            return None
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        raise Exception(f"Firestore API error {e.code}: {err}") from e

def get_all_songs():
    url = _url(f"{BASE}/songs", key=API_KEY, orderBy="uploaded_at desc")
    result = _request("GET", url)
    docs = result.get("documents", []) if result else []
    return [_make_doc(d) for d in docs]

def add_song(data):
    fields = _to_fields(data)
    fields["uploaded_at"] = {"timestampValue": "2026-05-21T00:00:00Z"}
    url = _url(f"{BASE}/songs", key=API_KEY)
    body = {"fields": fields}
    result = _request("POST", url, body)
    return result["name"].split("/")[-1]

def delete_song(song_id):
    url = _url(f"{BASE}/songs/{song_id}", key=API_KEY)
    _request("DELETE", url)

def get_all_playlists():
    url = _url(f"{BASE}/playlists", key=API_KEY)
    result = _request("GET", url)
    docs = result.get("documents", []) if result else []
    return [_make_doc(d) for d in docs]

def add_playlist(data):
    fields = _to_fields(data)
    fields["created_at"] = {"timestampValue": "2026-05-21T00:00:00Z"}
    fields["updated_at"] = {"timestampValue": "2026-05-21T00:00:00Z"}
    url = _url(f"{BASE}/playlists", key=API_KEY)
    body = {"fields": fields}
    result = _request("POST", url, body)
    return result["name"].split("/")[-1]

def update_playlist(playlist_id, data):
    fields = _to_fields(data)
    fields["updated_at"] = {"timestampValue": "2026-05-21T00:00:00Z"}
    doc_name = f"{BASE}/playlists/{playlist_id}"
    paths = [f"updateMask.fieldPaths={k}" for k in data.keys()]
    url = f"{doc_name}?key={API_KEY}&{'&'.join(paths)}"
    body = {"fields": fields}
    _request("PATCH", url, body)
