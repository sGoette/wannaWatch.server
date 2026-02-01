from pydantic import BaseModel
from typing import Optional
import requests
from urllib.parse import quote
from enum import StrEnum
from pathlib import Path
import time
import re

import logging
log = logging.getLogger(__name__)

class ROLE(StrEnum):
    ACTOR = 'ACTOR'
    DIRECTOR = 'DIRECTOR'

class SearchResult(BaseModel):
    id: str
    name: str

class PersonMetadata(BaseModel):
    name: str
    poster_url: Optional[str] = None
    role: ROLE

class CollectionData(BaseModel):
    title: str
    poster_file_name: Optional[str] = None
    poster_folder: Optional[Path] = None
    poster_url: Optional[str] = None

class Metadata(BaseModel):
    movie_title: Optional[str] = None
    genres: list[str] = []
    tags: list[str] = []
    collections: list[CollectionData] = []
    poster_url: Optional[str] = None
    people: list[PersonMetadata] = []

class IMDBAPISearchTitle(BaseModel):
    id: str
    type: str
    primaryTitle: str
    startYear: Optional[int] = None

class IMDBAPIImage(BaseModel):
    url: str
    width: int
    height: int

class IMDBAPIName(BaseModel):
    id: str
    displayName: str
    primaryImage: Optional[IMDBAPIImage] = None

class IMDBAPIInterest(BaseModel):
    id: str
    name: str
    primaryImage: Optional[IMDBAPIImage] = None
    description: Optional[str] = None
    isSubgenre: Optional[bool] = None
    similarInterests: Optional[list['IMDBAPIInterest']] = None

class IMDBAPITitle(BaseModel):
    id: str
    primaryTitle: str
    startYear: Optional[int]
    genres: list[str]
    primaryImage: Optional[IMDBAPIImage] = None
    directors: Optional[list[IMDBAPIName]] = None
    writers: Optional[list[IMDBAPIName]] = None
    stars: Optional[list[IMDBAPIName]] = None
    interests: list[IMDBAPIInterest]

IMDBAPIInterest.model_rebuild()
IMDBAPIName.model_rebuild()
IMDBAPITitle.model_rebuild()

def search(title: str) -> list[SearchResult]:
    imdb_id_pattern = re.search(r'-(tt\d{7}$)', title)
    if imdb_id_pattern:
        return [ SearchResult(id=str(imdb_id_pattern.group(1)), name=title) ]
    return findResults(search_name=title)


def findResults(search_name: str) -> list[SearchResult]:
    results: list[SearchResult] = []

    year_pattern = re.search(r'(\d{4})$', search_name)
    year = year_pattern.group(1) if year_pattern else None

    try: 
        time.sleep(2)
        search_response = requests.get("https://api.imdbapi.dev/search/titles?query=" + quote(search_name))
        search_response.raise_for_status()

        search_response_data = [IMDBAPISearchTitle(**d) for d in (search_response.json()["titles"] if search_response.json()["titles"] else [])]
        

        for item in search_response_data:
            name = item.primaryTitle
            if year:
                name += f" item.startYear"
            results.append(SearchResult(id=item.id, name=name))

    except Exception:
        log.exception(f"Unable to search for results for: {search_name}")

    return results


def fetch_metadata(search_result: SearchResult, potential_collections: list[str]) -> Optional[Metadata]:
    result = Metadata()

    try: 
        time.sleep(2)
        detail_info_response = requests.get("https://api.imdbapi.dev/titles/" + search_result.id)
        detail_info_response.raise_for_status()
        
        detail_info_data = IMDBAPITitle(**detail_info_response.json())

        result.movie_title = detail_info_data.primaryTitle
        result.genres = detail_info_data.genres
        result.tags = detail_info_data.genres
        
        for interest in detail_info_data.interests if detail_info_data.interests else []:
            time.sleep(2)
            interest_response = requests.get("https://api.imdbapi.dev/interests/" + interest.id)
            interest_response.raise_for_status()

            interest_data = IMDBAPIInterest(**interest_response.json())

            result.collections.append(CollectionData(title=interest_data.name, poster_url=interest_data.primaryImage.url if interest_data.primaryImage else None))

        result.poster_url = detail_info_data.primaryImage.url if detail_info_data.primaryImage else None

        for director in detail_info_data.directors if detail_info_data.directors else []:
            result.people.append(PersonMetadata(name=director.displayName, poster_url=director.primaryImage.url if director.primaryImage else None, role=ROLE.DIRECTOR))

        for star in detail_info_data.stars if detail_info_data.stars else []:
            result.people.append(PersonMetadata(name=star.displayName, poster_url=star.primaryImage.url if star.primaryImage else None, role=ROLE.ACTOR))

        return result

    except Exception:
        log.exception(f"Unable to search for metadata for {search_result.id}: {search_result.name}")

    return None