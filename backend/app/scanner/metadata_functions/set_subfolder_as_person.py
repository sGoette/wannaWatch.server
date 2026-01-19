import aiosqlite
from pathlib import Path

from app.config import DB_PATH
from backend.app.models.person import Person, ROLE
from app.scanner.metadata_functions.get_poster_from_folder import get_poster_from_folder

async def set_subfolder_as_person(person_name: str, path: Path, library_id: int, movie_id: int, poster_candidate_names: list[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM people WHERE name = ? AND library_id = ?", (person_name, library_id)) as cursor:
            person_row = await cursor.fetchone()

    if person_row: #Person already exists
        person = Person(**dict(person_row))
        person_id = person.id

        if person.poster_file_name == None:
            poster_file_name = get_poster_from_folder(folder_path=path, candidate_names=poster_candidate_names)
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("UPDATE people SET poster_file_name = ? WHERE id = ?", (poster_file_name, person_id))
                await db.commit()

    else: #Cas doesn't exist jet
        poster_file_name = poster_file_name = get_poster_from_folder(folder_path=path, candidate_names=poster_candidate_names)

        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("INSERT INTO people (name, poster_file_name, role, library_id) VALUES (?, ?, ?, ?)", (person_name, poster_file_name, ROLE.ACTOR, library_id)) as cursor:
                person_id = cursor.lastrowid
                await db.commit()

    if person_id:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM movies__people WHERE movie_id = ? AND person_id = ? ", (movie_id, person_id)) as select_cursor:
                movie__person_map = await select_cursor.fetchone()

            if not movie__person_map:
                await db.execute("INSERT INTO movies__people (movie_id, person_id) VALUES (?, ?)", (movie_id, person_id))

            await db.commit()