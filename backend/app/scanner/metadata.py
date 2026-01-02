import aiosqlite
from pathlib import Path
from typing import Optional, Tuple
import json as jsone
import shutil

from app.models.folder_collection_config import FolderCollectionConfig
from app.config import DB_PATH, GET_MEDIA_ROOT_FOLDER, POSTER_DIR
from app.models.movie import Movie
from app.scanner.media import get_file_hash
from app.models.collection import Collection

async def fetch_movie_metadata(movie_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)) as cursor:
            row = await cursor.fetchone()

    if row:
        movie = Movie(**dict(row))
        library_id = movie.library_id
        absolute_movie_path = Path(await GET_MEDIA_ROOT_FOLDER()).resolve() / movie.file_location

        folder_config = await find_folder_collection_config(absolute_movie_path)

        if folder_config:
            if folder_config[0].subfoldersAreCollections:
                current_folder_title = folder_config[1].name.title()
                async with aiosqlite.connect(DB_PATH) as db:
                    db.row_factory = aiosqlite.Row
                    async with db.execute("SELECT * FROM collections WHERE title = ? AND library_id = ?", (current_folder_title, library_id)) as cursor:
                        collection_row = await cursor.fetchone()

                if collection_row: #Collection already exists
                    collection = Collection(**dict(collection_row))
                    collection_id = collection.id

                    if collection.poster_file_name == '':
                        poster_file_name = get_poster_from_folder(folder_config[1]) or ""
                        async with aiosqlite.connect(DB_PATH) as db:
                            await db.execute("UPDATE collections SET poster_file_name = ? WHERE id = ?", (poster_file_name, collection_id))
                            await db.commit()

                else: #Collection doesn't exist jet
                    poster_file_name = get_poster_from_folder(folder_config[1]) or ""
                    async with aiosqlite.connect(DB_PATH) as db:
                        db.row_factory = aiosqlite.Row
                        async with db.execute("INSERT INTO collections (title, poster_file_name, library_id) VALUES (?, ?, ?)", (current_folder_title, poster_file_name, library_id)) as cursor:
                            collection_id = cursor.lastrowid
                            await db.commit()

                if collection_id:
                    async with aiosqlite.connect(DB_PATH) as db:
                        db.row_factory = aiosqlite.Row
                        async with db.execute("SELECT * FROM movies__collections WHERE movie_id = ? AND collection_id = ?", (movie_id, collection_id)) as select_cursor: 
                            movie__collection_map = await select_cursor.fetchone()
                        
                        if not movie__collection_map:
                            await db.execute("INSERT INTO movies__collections (movie_id, collection_id) VALUES (?, ?)", (movie_id, collection_id))

                        await db.commit()


                

async def find_folder_collection_config(start_path: Path) -> Optional[Tuple[FolderCollectionConfig, Path]]:
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    current = start_path.parent if start_path.is_file() else start_path
    last_folder = None
    while True:
        candidate = current / '__wannawatch.json'
        if candidate.is_file():
            with candidate.open("r", encoding="utf-8") as f:
                data = jsone.load(f)
            return FolderCollectionConfig(**data), last_folder or current
        
        if current == MEDIA_ROOT_FOLDER:
            break
        if current.parent == current:
            break

        last_folder = current
        current = current.parent
        
    return None

def get_poster_from_folder(folder_path: Path) -> Optional[str]:
    POSTER_CANDIDATE_NAMES = ['folder' 'cover', 'poster', 'thumb', 'thumbnail', 'collection']
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    for path in Path(folder_path).iterdir():
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and path.stem.lower() in POSTER_CANDIDATE_NAMES:
            poster_file_name = f"{get_file_hash(str(path))}{path.suffix}"
            shutil.copy2(path, POSTER_DIR / poster_file_name)
            return poster_file_name
    
    return None