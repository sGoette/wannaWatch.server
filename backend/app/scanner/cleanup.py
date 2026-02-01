import aiosqlite
from pathlib import Path
from app.config import DB_PATH, GET_MEDIA_ROOT_FOLDER, POSTER_DIR
from app.models.movie import Movie
from app.models.collection import Collection

import logging
log = logging.getLogger(__name__)

async def cleanup_orphaned_posters():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT poster_file_name FROM movies WHERE poster_file_name IS NOT NULL") as movie_poster_cursor:
            movie_poster_rows = await movie_poster_cursor.fetchall()

        async with db.execute("SELECT poster_file_name FROM collections WHERE poster_file_name IS NOT NULL") as collection_poster_cursor: 
            collection_poster_rows = await collection_poster_cursor.fetchall()

        async with db.execute("SELECT poster_file_name FROM people WHERE poster_file_name IS NOT NULL") as people_poster_cursor:
            people_poster_rows = await people_poster_cursor.fetchall()

    poster_file_names = [str(row["poster_file_name"]) for row in movie_poster_rows if row["poster_file_name"]] + [str(row["poster_file_name"]) for row in collection_poster_rows if row["poster_file_name"]] + [str(row["poster_file_name"]) for row in people_poster_rows if row["poster_file_name"]]
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
            except Exception:
                log.exception(f"[Scanner] Could not delete orphan poster {entry}:")

    if removed:
        log.info(f"[Scanner] Removed {removed} orphan posters")

async def cleanup_orphaned_movies ():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies") as cursor:
            movie_rows = await cursor.fetchall()

            movies = [Movie(**dict(row)) for row in movie_rows]
            MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()

            for movie in movies:
                if not Path(MEDIA_ROOT_FOLDER, movie.file_location).resolve().is_file(): #We formated the file_location to utf-8, might be a problem here
                    async with aiosqlite.connect(DB_PATH) as db:
                        db.row_factory = aiosqlite.Row #TODO: add forein keys, so other objects gets deleted as well. 
                        await db.execute("DELETE FROM movies WHERE id = ?", (movie.id,))
                        await db.commit()

async def cleanup_orphaned_collections ():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM collections") as collection_cursor:
            collection_rows = await collection_cursor.fetchall()

            collections = [Collection(**dict(row)) for row in collection_rows]

            for collection in collections:
                async with db.execute("SELECT * FROM movies__collections WHERE collection_id = ?", (collection.id,)) as movie__collection_cursor:
                    movie__collection_row = await movie__collection_cursor.fetchone()

                if movie__collection_row is None:
                    await db.execute("DELETE FROM collections WHERE id = ?", (collection.id,))
                    await db.commit()