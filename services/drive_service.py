import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CONFIG_DIR = os.path.dirname(os.path.dirname(__file__))
CLIENT_SECRET = os.path.join(CONFIG_DIR, "drive_oauth.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "drive_token.json")
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def _get_credentials():
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
            return creds

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    return creds

def upload_mp3(file_path):
    name = os.path.basename(file_path)
    creds = _get_credentials()
    service = build("drive", "v3", credentials=creds)

    media = MediaFileUpload(file_path, mimetype="audio/mpeg", resumable=True)
    file_metadata = {"name": name}
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = file["id"]

    service.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return {
        "file_id": file_id,
        "download_url": f"https://drive.usercontent.google.com/download?id={file_id}&export=download",
    }
