import os
from pathlib import Path

from app.config import GET_MEDIA_ROOT_FOLDER, VIDEO_EXTENSIONS
from app.models.library import Library
from app.scanner.movie import process_movie
from app.scanner.metadata import fetch_movie_metadata

import logging
log = logging.getLogger(__name__)

async def scan_library(library: Library, ignore_existing_metadata: bool):
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    library_media_folder = library.media_folder

    MEDIA_ROOT_FOLDER = Path(MEDIA_ROOT_FOLDER).resolve()
    absolute_library_path = (MEDIA_ROOT_FOLDER / library_media_folder)

    log.info(f"[Scanner] Scanning library {library.id}: {absolute_library_path}")

    for dirpath, _, filenames in os.walk(absolute_library_path):
        for filename in filenames:
            if not os.path.splitext(filename)[1].lower() in VIDEO_EXTENSIONS:
                continue
            
            absolte_file_path = (Path(dirpath).resolve() / filename)
            movie = await process_movie(absolute_file_path=absolte_file_path, library_id=library.id)

            if movie and (movie.metadata_last_updated is None or ignore_existing_metadata is True):
                await fetch_movie_metadata(movie=movie, absolute_path=absolte_file_path) #separate scanning and updating metadata. fist scan all files, then fetch the metadata