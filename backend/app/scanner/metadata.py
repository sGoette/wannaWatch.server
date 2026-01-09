import aiosqlite
from pathlib import Path
from typing import Optional, Tuple
import json as jsone
import shutil
from typing import List

from app.models.folder_collection_config import FolderCollectionConfig, FolderCollectionConfig_Path
from app.config import DB_PATH, GET_MEDIA_ROOT_FOLDER, POSTER_DIR
from app.models.movie import Movie
from app.scanner.media import get_file_hash
from app.models.collection import Collection
from app.models.cast import Cast, Role

async def fetch_movie_metadata(movie_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)) as cursor:
            row = await cursor.fetchone()

    if row:
        movie = Movie(**dict(row))
        library_id = movie.library_id
        absolute_movie_path = Path(await GET_MEDIA_ROOT_FOLDER()).resolve() / movie.file_location

        configs = await find_folder_collection_config(absolute_movie_path)

        COLLECTION_POSTER_CANDIDATE_NAMES = ['folder' 'cover', 'poster', 'thumb', 'thumbnail', 'collection']

        for config in configs:
            if config.data.subfoldersAreCollections:
                await set_subfolder_as_collection(folder_config=config, library_id=library_id, movie_id=movie_id, poster_candidate_names=COLLECTION_POSTER_CANDIDATE_NAMES)

            if config.data.subfoldersAreCast:
                current_folder_title = config.path.name.title()
                await set_subfolder_as_cast(cast_name=current_folder_title, path=config.path, library_id=library_id, movie_id=movie_id, poster_candidate_names=[current_folder_title.lower()])

            for additional_cast in config.data.folderCast:
                await set_subfolder_as_cast(cast_name=additional_cast, path=config.path, library_id=library_id, movie_id=movie_id, poster_candidate_names=[additional_cast.lower()])

async def find_folder_collection_config(start_path: Path) -> List[FolderCollectionConfig_Path]:
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    current = start_path.parent if start_path.is_file() else start_path
    last_folder = None
    configs: List[FolderCollectionConfig_Path] = []

    while True:
        candidate = current / '__wannawatch.json'
        if candidate.is_file():
            with candidate.open("r", encoding="utf-8") as f:
                data = jsone.load(f)
                entry = FolderCollectionConfig_Path(data=FolderCollectionConfig(**data), path=last_folder or current)
                configs.append(entry)
        
        if current == MEDIA_ROOT_FOLDER:
            break
        if current.parent == current:
            break

        last_folder = current
        current = current.parent
        
    return configs

def get_poster_from_folder(folder_path: Path, poster_candidate_names:list[str]) -> Optional[str]:
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    for path in Path(folder_path).iterdir():
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and path.stem.lower() in poster_candidate_names:
            poster_file_name = f"{get_file_hash(str(path))}{path.suffix}"
            shutil.copy2(path, POSTER_DIR / poster_file_name)
            return poster_file_name
    
    return None

async def set_subfolder_as_collection(folder_config: FolderCollectionConfig_Path, library_id: int, movie_id: int, poster_candidate_names: list[str]):
    current_folder_title = folder_config.path.name.title()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM collections WHERE title = ? AND library_id = ?", (current_folder_title, library_id)) as cursor:
            collection_row = await cursor.fetchone()

    if collection_row: #Collection already exists
        collection = Collection(**dict(collection_row))
        collection_id = collection.id

        if collection.poster_file_name == "":
            poster_file_name = get_poster_from_folder(folder_path=folder_config.path, poster_candidate_names=poster_candidate_names) or ""
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("UPDATE collections SET poster_file_name = ? WHERE id = ?", (poster_file_name, collection_id))
                await db.commit()

    else: #Collection doesn't exist jet
        poster_file_name = get_poster_from_folder(folder_path=folder_config.path, poster_candidate_names=poster_candidate_names) or ""
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

async def set_subfolder_as_cast(cast_name: str, path: Path, library_id: int, movie_id: int, poster_candidate_names: list[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM cast WHERE name = ? AND library_id = ?", (cast_name, library_id)) as cursor:
            cast_row = await cursor.fetchone()

    if cast_row: #Cast already exists
        cast = Cast(**dict(cast_row))
        cast_id = cast.id

        if cast.poster_file_name == "":
            poster_file_name = get_poster_from_folder(folder_path=path, poster_candidate_names=poster_candidate_names) or ""
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("UPDATE cast SET poster_file_name = ? WHERE id = ?", (poster_file_name, cast_id))
                await db.commit()

    else: #Cas doesn't exist jet
        poster_file_name = poster_file_name = get_poster_from_folder(folder_path=path, poster_candidate_names=poster_candidate_names) or ""

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("INSERT INTO cast (name, poster_file_name, role, library_id) VALUES (?, ?, ?, ?)", (cast_name, poster_file_name, Role.ACTOR, library_id)) as cursor:
                cast_id = cursor.lastrowid
                await db.commit()

    if cast_id:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM movies__cast WHERE movie_id = ? AND cast_id = ? ", (movie_id, cast_id)) as select_cursor:
                movie__cast_map = await select_cursor.fetchone()

            if not movie__cast_map:
                await db.execute("INSERT INTO movies__cast (movie_id, cast_id) VALUES (?, ?)", (movie_id, cast_id))

            await db.commit()