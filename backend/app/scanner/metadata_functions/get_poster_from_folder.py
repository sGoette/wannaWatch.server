from pathlib import Path
from typing import Optional
import shutil

from app.scanner.media import get_file_hash
from app.config import POSTER_DIR

def get_poster_from_folder(folder_path: Path, candidate_names:list[str]) -> Optional[str]:
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    for path in Path(folder_path).iterdir():
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and path.stem.lower() in candidate_names:
            poster_file_name = f"{get_file_hash(str(path))}{path.suffix}"
            shutil.copy2(path, POSTER_DIR / poster_file_name)
            return poster_file_name
    
    return None