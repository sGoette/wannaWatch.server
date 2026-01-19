import aiosqlite

from app.config import DB_PATH
from app.models.movie import Movie
from app.models.metadata import PersonMetadata
from app.models.person import Person, ROLE
from app.scanner.metadata_functions.get_poster_from_url import get_poster_from_url

async def add_person_to_movie(person_metadata: PersonMetadata, movie: Movie):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM people WHERE name = ? AND library_id = ?", (person_metadata.name, movie.library_id)) as select_cursor1: #TODO: compare lowercase with lowercase
            person_row = await select_cursor1.fetchone()
            
        if person_row is None:
            async with db.execute("INSERT INTO people (name, role, library_id) VALUES (?, ?, ?)", (person_metadata.name, ROLE.ACTOR, movie.library_id)) as insert_cursor:
                person_id = insert_cursor.lastrowid
                await db.commit()
                
            async with db.execute("SELECT * FROM people WHERE id = ?",(person_id,)) as select_cursor2:
                person_row = await select_cursor2.fetchone()
                if person_row is not None:
                    person = Person(**person_row)

        else:
            person = Person(**person_row)

        if person:
            async with db.execute("SELECT * FROM movies__people WHERE person_id = ? AND movie_id = ?", (person.id, movie.id)) as movies__people_cursor:
                movies__person_row = await movies__people_cursor.fetchone()

            if movies__person_row is None:
                await db.execute("INSERT INTO movies__people (movie_id, person_id) VALUES (?, ?)", (movie.id, person.id))
                await db.commit()

            if person.poster_file_name is None and person_metadata.poster_url:
                poster_file_name = get_poster_from_url(url=person_metadata.poster_url)

                if poster_file_name:
                    await db.execute("UPDATE people SET poster_file_name = ? WHERE id = ?", (poster_file_name, person.id))

        