import requests
from pathlib import Path
import mimetypes
from typing import Optional

from app.scanner.media import get_file_hash
from app.config import POSTER_DIR

def get_poster_from_url(url: str) -> Optional[str]:
    try: 
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").split(";")[0]
        extension = mimetypes.guess_extension(content_type) or ".bin"

        poster_file_name = f"{get_file_hash(str(url))}{extension}"
        target = POSTER_DIR / poster_file_name

        target.write_bytes(response.content)
        return poster_file_name
    except Exception as e:
        print(e)
        return None