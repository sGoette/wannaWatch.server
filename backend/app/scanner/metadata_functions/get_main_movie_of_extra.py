from pathlib import Path
from typing import Optional
import aiosqlite

import logging
log = logging.getLogger(__name__)

from app.models.movie import Movie
from app.config import GET_MEDIA_ROOT_FOLDER, DB_PATH, VIDEO_EXTENSIONS
from app.scanner.movie import process_movie

async def get_main_movie_of_extra(absolute_file_path: Path, main_movie_file_name: str, library_id: int) -> Optional[Movie]:
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    relative_file_path = absolute_file_path.relative_to(MEDIA_ROOT_FOLDER)
    main_movie_file_location = f"{relative_file_path.parent}/{main_movie_file_name}"

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE file_location LIKE ? AND library_id = ?", (f"{main_movie_file_location}%", library_id)) as cursor:
            main_movie_row = await cursor.fetchone()

            if main_movie_row:
                return Movie(**main_movie_row)

            else:
                for ext in VIDEO_EXTENSIONS:
                    file_path = Path(MEDIA_ROOT_FOLDER).joinpath(f"{main_movie_file_location}{ext}")
                    
                    if file_path.is_file():
                        movie = await process_movie(absolute_file_path=file_path.absolute(), library_id=library_id)

                        return movie
                    
    return None