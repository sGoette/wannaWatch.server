import aiosqlite
from pathlib import Path
from typing import Optional

from app.models.folder_collection_config import FolderCollectionConfig_Path
from app.config import DB_PATH, COLLECTION_POSTER_CANDIDATE_NAMES
from app.models.collection import Collection
from app.models.movie import Movie
from app.scanner.metadata_functions.get_poster_from_folder import get_poster_from_folder, get_poster_from_file_name
from app.models.collection import CollectionData
from app.scanner.metadata_functions.get_poster_from_url import get_poster_from_url

async def add_collection_to_movie(collection_data: CollectionData, movie: Movie):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM collections WHERE title = ? AND library_id = ?", (collection_data.title, movie.library_id)) as select_cursor1: 
            collection_row = await select_cursor1.fetchone()

        if collection_row is None: #Collection doesn't exist jet
            async with db.execute("INSERT INTO collections (title, library_id) VALUES (?, ?)", (collection_data.title, movie.library_id)) as insert_cursor:
                collection_id = insert_cursor.lastrowid
                await db.commit()

            async with db.execute("SELECT * FROM collections WHERE id = ?", (collection_id,)) as select_cursor2:
                collection_row = await select_cursor2.fetchone()
                if collection_row is not None:
                    collection = Collection(**collection_row)

        else:
            collection = Collection(**collection_row)

        if collection:
            async with db.execute("SELECT * FROM movies__collections WHERE movie_id = ? AND collection_id = ?", (movie.id, collection.id)) as movies__collection_cursor: 
                movie__collection_row = await movies__collection_cursor.fetchone()
            
            if movie__collection_row is None:
                await db.execute("INSERT INTO movies__collections (movie_id, collection_id) VALUES (?, ?)", (movie.id, collection.id))
                await db.commit()

            if collection.poster_file_name is None:
                poster_file_name: Optional[str] = None
                if collection_data.poster_url:
                    poster_file_name = get_poster_from_url(collection_data.poster_url)
                elif collection_data.poster_file_name and Path(collection_data.poster_file_name).is_file(): #TODO: Check if file is an image and if it is inside the media dir
                    poster_file_name = get_poster_from_file_name(Path(collection_data.poster_file_name))
                elif collection_data.poster_folder:
                    poster_file_name = get_poster_from_folder(folder_path=collection_data.poster_folder, candidate_names=COLLECTION_POSTER_CANDIDATE_NAMES)

                await db.execute("UPDATE collections SET poster_file_name = ? WHERE id = ?", (poster_file_name, collection.id))
                await db.commit()