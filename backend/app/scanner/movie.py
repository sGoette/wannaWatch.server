import os
import aiosqlite
from typing import Optional
from pathlib import Path

import logging
log = logging.getLogger(__name__)

from app.config import DB_PATH, GET_MEDIA_ROOT_FOLDER
from app.scanner.media import get_video_file_metadata
from app.models.movie import Movie

async def process_movie(absolute_file_path: Path, library_id: int) -> Optional[Movie]:
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    relative_path = os.path.relpath(absolute_file_path, MEDIA_ROOT_FOLDER)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE file_location = ? AND library_id = ?", (relative_path, library_id)) as cursor:
            existing_movie_row = await cursor.fetchone()

    if not existing_movie_row:
        return await add_movie_to_db(library_id=library_id, absolute_file_path=absolute_file_path)

    else:
        return Movie(**dict(existing_movie_row))

async def add_movie_to_db(library_id: int, absolute_file_path: Path) -> Optional[Movie]:
    relative_path = Path(os.path.relpath(absolute_file_path, await GET_MEDIA_ROOT_FOLDER()))
    movie_title = absolute_file_path.stem.title()
    
    length_in_seconds: float = 0.0
    width: int = 0
    height: int = 0
    codec: str = ""
    format_name: str = ""

    try:
        file_metadata = await get_video_file_metadata(absolute_file_path)
        format_info = file_metadata.get("format", {})
        streams = file_metadata.get("streams", [])

        video_steam = next((s for s in streams if s["codec_type"] == "video"), {})
        length_in_seconds = float(format_info.get("duration", 0))
        width = int(video_steam.get("width", 0))
        height = int(video_steam.get("height", 0))
        codec = video_steam.get("codec_name", "")
        format_name = format_info.get("format_name", "")
    except Exception:
        log.exception(f"[Scanner] Failed to get metadata for {absolute_file_path}")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
INSERT INTO movies (title, file_location, length_in_seconds, width, height, codec, format, library_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (movie_title, str(relative_path), length_in_seconds, width, height, codec, format_name, library_id)) as cursor: 
            new_movie_id = cursor.lastrowid
        await db.commit()

        if new_movie_id:
            async with db.execute("SELECT * FROM movies WHERE id = ?", (new_movie_id,)) as select_cursor:
                movie_row = await select_cursor.fetchone()
                if movie_row:
                    return Movie(**movie_row)
        else:
            return None