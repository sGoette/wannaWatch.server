import aiosqlite

from app.models.folder_collection_config import FolderCollectionConfig_Path
from app.config import DB_PATH, COLLECTION_POSTER_CANDIDATE_NAMES
from app.models.collection import Collection
from app.models.movie import Movie
from app.scanner.metadata_functions.get_poster_from_folder import get_poster_from_folder

async def set_subfolder_as_collection(folder_config: FolderCollectionConfig_Path, library_id: int, movie_id: int):
    if folder_config.childPath:
        current_folder_title = folder_config.childPath.name.title()
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM collections WHERE title = ? AND library_id = ?", (current_folder_title, library_id)) as cursor:
                collection_row = await cursor.fetchone()

        if collection_row: #Collection already exists
            collection = Collection(**dict(collection_row))
            collection_id = collection.id

            if collection.poster_file_name == None:
                poster_file_name = get_poster_from_folder(folder_path=folder_config.childPath, candidate_names=COLLECTION_POSTER_CANDIDATE_NAMES)
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute("UPDATE collections SET poster_file_name = ? WHERE id = ?", (poster_file_name, collection_id))
                    await db.commit()

        else: #Collection doesn't exist jet
            poster_file_name = get_poster_from_folder(folder_path=folder_config.childPath, candidate_names=COLLECTION_POSTER_CANDIDATE_NAMES)
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




async def add_collection_to_movie(collection_title: str, movie: Movie):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM collections WHERE title = ? AND library_id = ?", (collection_title, movie.library_id)) as select_cursor1: 
            collection_row = await select_cursor1.fetchone()

        if collection_row is None: #Collection doesn't exist jet
            async with db.execute("INSERT INTO collections (title, library_id) VALUES (?, ?)", (collection_title, movie.library_id)) as insert_cursor:
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