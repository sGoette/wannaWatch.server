import aiosqlite

from app.config import DB_PATH
from app.models.movie import Movie
from app.models.metadata import Actor
from app.models.cast import Cast, ROLE
from app.scanner.metadata_functions.get_poster_from_url import get_poster_from_url

async def add_actor_to_movie(actor: Actor, movie: Movie):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM cast WHERE name = ? AND library_id = ?", (actor.name, movie.library_id)) as select_cursor1: #TODO: compare lowercase with lowercase
            cast_row = await select_cursor1.fetchone()
            
        if cast_row is None:
            async with db.execute("INSERT INTO cast (name, role, library_id) VALUES (?, ?, ?)", (actor.name, ROLE.ACTOR, movie.library_id)) as insert_cursor:
                cast_id = insert_cursor.lastrowid
                await db.commit()
                
            async with db.execute("SELECT * FROM cast WHERE id = ?",(cast_id,)) as select_cursor2:
                cast_row = await select_cursor2.fetchone()
                if cast_row is not None:
                    cast = Cast(**cast_row)

        else:
            cast = Cast(**cast_row)

        if cast:
            async with db.execute("SELECT * FROM movies__cast WHERE cast_id = ? AND movie_id = ?", (cast.id, movie.id)) as movies__cast_cursor:
                movies__cast_row = await movies__cast_cursor.fetchone()

            if movies__cast_row is None:
                await db.execute("INSERT INTO movies__cast (movie_id, cast_id) VALUES (?, ?)", (movie.id, cast.id))
                await db.commit()

            if cast.poster_file_name is None and actor.poster_url:
                poster_file_name = get_poster_from_url(url=actor.poster_url)

                if poster_file_name:
                    await db.execute("UPDATE cast SET poster_file_name = ? WHERE id = ?", (poster_file_name, cast.id))

        