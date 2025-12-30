import os
import aiosqlite
from pathlib import Path
from app.config import DB_PATH, GET_MEDIA_ROOT_FOLDER, POSTER_DIR
from app.models.movie import Movie

async def cleanup_orphaned_posters():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT poster_file_name FROM movies WHERE poster_file_name IS NOT NULL") as cursor:
            rows = await cursor.fetchall()

    poster_file_names = [str(row["poster_file_name"]) for row in rows if row["poster_file_name"]]
    referenced = set()

    for poster_file_name in poster_file_names:
        absolute_poster_path = Path(POSTER_DIR, poster_file_name).resolve()
        if absolute_poster_path.is_relative_to(POSTER_DIR):
            referenced.add(absolute_poster_path)

    removed = 0

    for entry in POSTER_DIR.iterdir():
        if entry.is_file() and entry not in referenced:
            try:
                entry.unlink()
                removed += 1
            except Exception as e:
                print(f"[Scanner] Could not delete orphan poster {entry}: {e}")

    if removed:
        print(f"[Scanner] Removed {removed} orphan posters")