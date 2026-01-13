import aiosqlite
from pathlib import Path

from app.config import DB_PATH
from app.models.cast import Cast, Role
from app.scanner.metadata_functions.get_poster_from_folder import get_poster_from_folder

async def set_subfolder_as_cast(cast_name: str, path: Path, library_id: int, movie_id: int, poster_candidate_names: list[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM cast WHERE name = ? AND library_id = ?", (cast_name, library_id)) as cursor:
            cast_row = await cursor.fetchone()

    if cast_row: #Cast already exists
        cast = Cast(**dict(cast_row))
        cast_id = cast.id

        if cast.poster_file_name == None:
            poster_file_name = get_poster_from_folder(folder_path=path, candidate_names=poster_candidate_names)
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("UPDATE cast SET poster_file_name = ? WHERE id = ?", (poster_file_name, cast_id))
                await db.commit()

    else: #Cas doesn't exist jet
        poster_file_name = poster_file_name = get_poster_from_folder(folder_path=path, candidate_names=poster_candidate_names)

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