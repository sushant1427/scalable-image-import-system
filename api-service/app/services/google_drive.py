import re
import requests
from typing import List, Dict, Optional

FOLDER_PATTERNS = [
    r"drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)",
    r"drive\.google\.com/folderview\?id=([a-zA-Z0-9_-]+)",
]

def extract_folder_id(folder_url: str) -> Optional[str]:
    for pat in FOLDER_PATTERNS:
        match_object = re.search(pat, folder_url)
        if match_object:
            return match_object.group(1)
    return None

def list_images_in_folder(folder_id: str, api_key: str) -> List[Dict]:
    # Google Drive API v3 files.list with public access via API key
    url = "https://www.googleapis.com/drive/v3/files"
    query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false"
    fields = "nextPageToken, files(id,name,mimeType,size)"
    params = {
        "q": query,
        "fields": fields,
        "pageSize": 1000,
        "key": api_key,
        "supportsAllDrives": "true",
        "includeItemsFromAllDrives": "true",
    }

    files: List[Dict] = []
    page_token = None
    while True:
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Drive API list failed: {resp.status_code} {resp.text[:200]}")
        data = resp.json()
        files.extend(data.get("files", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return files
