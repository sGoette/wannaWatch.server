import os
import aiosqlite
from typing import Optional

from app.config import DB_PATH, GET_MEDIA_ROOT_FOLDER
from app.scanner.media import get_video_file_metadata
from app.models.movie import Movie

async def process_movie(dirpath: str, filename: str, library_id: int) -> Optional[Movie]:
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    absolute_path = os.path.join(dirpath, filename)
    relative_path = os.path.relpath(absolute_path, MEDIA_ROOT_FOLDER)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE file_location = ? AND library_id = ?", (relative_path, library_id)) as cursor:
            existing_movie_row = await cursor.fetchone()

    if not existing_movie_row:
        return await add_movie_to_db(library_id=library_id, absolute_path=absolute_path)

    else:
        return Movie(**dict(existing_movie_row))

async def add_movie_to_db(library_id: int, absolute_path: str) -> Optional[Movie]:
    filename = os.path.basename(absolute_path)
    relative_path = os.path.relpath(absolute_path, await GET_MEDIA_ROOT_FOLDER())
    movie_title = filename.rsplit('.', 1)[0].title()

    length_in_seconds: float = 0.0
    width: int = 0
    height: int = 0
    codec: str = ""
    format_name: str = ""

    try:
        file_metadata = await get_video_file_metadata(absolute_path)
        format_info = file_metadata.get("format", {})
        streams = file_metadata.get("streams", [])

        video_steam = next((s for s in streams if s["codec_type"] == "video"), {})
        length_in_seconds = float(format_info.get("duration", 0))
        width = int(video_steam.get("width", 0))
        height = int(video_steam.get("height", 0))
        codec = video_steam.get("codec_name", "")
        format_name = format_info.get("format_name", "")
    except Exception as e:
        print(f"[Scanner] Failed to get metadata for {absolute_path}: {e}")

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
INSERT INTO movies (title, file_location, length_in_seconds, width, height, codec, format, poster_file_name, library_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (movie_title, relative_path, length_in_seconds, width, height, codec, format_name, "", library_id)) as cursor: 
            new_movie_id = cursor.lastrowid
        await db.commit()

        if new_movie_id:
            async with db.execute("SELECT * FROM movies WHERE id = ?", (new_movie_id,)) as select_cursor:
                movie_row = await select_cursor.fetchone()
                if movie_row:
                    return Movie(**movie_row)
        else:
            return None