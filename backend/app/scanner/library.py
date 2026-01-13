import os
from pathlib import Path

from app.config import GET_MEDIA_ROOT_FOLDER, VIDEO_EXTENSIONS
from app.models.library import Library
from app.scanner.movie import process_movie
from app.scanner.metadata import fetch_movie_metadata

async def scan_library(library: Library):
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    library_media_folder = library.media_folder

    MEDIA_ROOT_FOLDER = Path(MEDIA_ROOT_FOLDER).resolve()
    absolute_library_path = (MEDIA_ROOT_FOLDER / library_media_folder)

    print(f"[Scanner] Scanning library {library.id}: {absolute_library_path}")

    for dirpath, _, filenames in os.walk(absolute_library_path):
        for filename in filenames:
            if not os.path.splitext(filename)[1].lower() in VIDEO_EXTENSIONS:
                continue

            movie = await process_movie(dirpath=dirpath, filename=filename, library_id=library.id)

            if movie and movie.metadata_last_updated is None:
                await fetch_movie_metadata(movie=movie, absolute_path=os.path.join(dirpath, filename)) #separate scanning and updating metadata. fist scan all files, then fetch the metadata