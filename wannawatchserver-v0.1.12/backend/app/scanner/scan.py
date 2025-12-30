import os
import aiosqlite
from typing import Optional
from pathlib import Path
from app.config import DB_PATH, GET_MEDIA_ROOT_FOLDER
from app.scanner.jobs import ScanJob
from app.models.library import Library
from app.scanner.media import get_video_metadata, generate_poster
from app.scanner.cleanup import cleanup_orphaned_posters

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'}

async def scan_libraries(job: ScanJob):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")

        if job.library_id:
            cursor = await db.execute("SELECT * FROM libraries WHERE id = ?", (job.library_id,))
        else: 
            cursor = await db.execute("SELECT * FROM libraries")

        rows = await cursor.fetchall()
        await cursor.close()

        libraries = [Library(**dict(row)) for row in rows]

        for library in libraries:
            await scan_library(library)

        #Cleanup orphaned posters after scanning
        await cleanup_orphaned_posters()

        
async def scan_library(library: Library):
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    library_media_folder = library.media_folder
    library_id = library.id

    MEDIA_ROOT_FOLDER = Path(await GET_MEDIA_ROOT_FOLDER()).resolve()
    absolute_library_path = (MEDIA_ROOT_FOLDER / library_media_folder)

    print(f"[Scanner] Scanning library {library_id}: {absolute_library_path}")

    for dirpath, _, filenames in os.walk(absolute_library_path):
        for filename in filenames:
            if not is_video_file(filename):
                continue

            full_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(full_path, MEDIA_ROOT_FOLDER)
            async with aiosqlite.connect(DB_PATH) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("SELECT * FROM movies WHERE file_location = ? AND library_id = ?", (relative_path, library_id))
                existing_movie = await cursor.fetchone()
                await cursor.close()

            if existing_movie:
                continue  # Movie already exists in the database
            
            await upsert_movie(library_id, full_path)

def is_video_file(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in VIDEO_EXTENSIONS

async def upsert_movie(library_id: int, path: str):
    filename = os.path.basename(path)
    relative_path = os.path.relpath(path, await GET_MEDIA_ROOT_FOLDER())
    movie_title = filename.rsplit('.', 1)[0].title()
    try:
        metadata = await get_video_metadata(path)
        format_info = metadata.get("format", {})
        streams = metadata.get("streams", [])

        video_steam = next((s for s in streams if s["codec_type"] == "video"), {})
        length_in_seconds = float(format_info.get("duration", 0))
        width = int(video_steam.get("width", 0))
        height = int(video_steam.get("height", 0))
        codec = video_steam.get("codec_name", "")
        format_name = format_info.get("format_name", "")
    except Exception as e:
        print(f"[Scanner] Failed to get metadata for {path}: {e}")
        duration = width = height = 0
        codec = None
        format = None

    try:
        poster = await generate_poster(path, length_in_seconds)
    except Exception as e:
        print(f"[Scanner] Failed to generate poster for {path}: {e}")
        poster = None

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
INSERT INTO movies (title, file_location, length_in_seconds, width, height, codec, format, poster_file_name, library_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (movie_title, relative_path, length_in_seconds, width, height, codec, format_name, poster, library_id))
        await db.commit()
        await db.close()