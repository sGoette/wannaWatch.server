import aiosqlite
from pathlib import Path
import importlib.util
from typing import Optional
from Levenshtein import ratio

import logging
log = logging.getLogger(__name__)

from app.config import GET_MEDIA_ROOT_FOLDER, DB_PATH
from app.models.movie import Movie
from app.models.metadata import Metadata, SearchResult
from app.scanner.media import generate_poster

from app.scanner.metadata_functions.folder_collection_config import find_folder_collection_config
from app.scanner.metadata_functions.set_subfolder_as_collection import set_subfolder_as_collection, add_collection_to_movie
from app.scanner.metadata_functions.set_subfolder_as_cast import set_subfolder_as_cast
from app.scanner.metadata_functions.get_poster_from_url import get_poster_from_url
from app.scanner.metadata_functions.add_actor_to_movie import add_actor_to_movie

async def fetch_movie_metadata(movie: Movie, absolute_path: str):
    absolute_movie_path = Path(await GET_MEDIA_ROOT_FOLDER()).resolve() / movie.file_location

    configs = await find_folder_collection_config(absolute_movie_path)

    for config in configs:
        if config.data.subfoldersAreCollections:
            await set_subfolder_as_collection(folder_config=config, library_id=movie.library_id, movie_id=movie.id)

        if config.data.subfoldersAreCast and config.childPath:
            current_folder_title = config.childPath.name.title()
            await set_subfolder_as_cast(cast_name=current_folder_title, path=config.childPath, library_id=movie.library_id, movie_id=movie.id, poster_candidate_names=[current_folder_title.lower()])

        if config.childPath:
            for additional_cast in config.data.folderCast:
                await set_subfolder_as_cast(cast_name=additional_cast, path=config.childPath, library_id=movie.library_id, movie_id=movie.id, poster_candidate_names=[additional_cast.lower()])

        if config.data.useScraper:
            scraper_spec = importlib.util.spec_from_file_location("scraper", config.currentPath / "__wannawatch.py")
            if scraper_spec and scraper_spec.loader:
                scraper = importlib.util.module_from_spec(spec=scraper_spec)
                scraper_spec.loader.exec_module(scraper)

                search_results: list[SearchResult] = scraper.search(title=movie.title)

                if len(search_results) > 0:
                    best_result: SearchResult = max(search_results, key=lambda r: ratio(r.name, movie.title))
                    
                    if best_result:
                        metadata: Optional[Metadata] = scraper.fetch_metadata(search_result=search_results[0], potential_collections=config.data.potential_collections)

                        if metadata:
                            if metadata.poster_url:
                                poster_file_name = get_poster_from_url(url=metadata.poster_url)
                            else: 
                                poster_file_name = movie.poster_file_name
                                
                            async with aiosqlite.connect(DB_PATH) as db:
                                await db.execute("UPDATE movies SET title = ?, poster_file_name = ?, metadata_last_updated = unixepoch() WHERE id = ?", (metadata.movie_title, poster_file_name, movie.id))
                                await db.commit()
                                
                                movie.title = metadata.movie_title or movie.title
                                movie.poster_file_name = poster_file_name

                            for actor in metadata.cast:
                                await add_actor_to_movie(actor=actor, movie=movie)

                            for collection in metadata.collections:
                                await add_collection_to_movie(collection_data=collection, movie=movie)
                            
    if movie.poster_file_name is None:
        try:
            if movie.length_in_seconds:
                poster_from_stil = await generate_poster(path=absolute_path, length_in_seconds=movie.length_in_seconds)
                async with aiosqlite.connect(DB_PATH) as db:
                    await db.execute("UPDATE movies SET poster_file_name = ?, metadata_last_updated = unixepoch() WHERE id = ?", (poster_from_stil, movie.id))
                    await db.commit()
        except Exception:
            log.exception(f"[Scanner] Failed to generate poster for {absolute_path}")
                        