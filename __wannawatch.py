from pydantic import BaseModel
from typing import Optional
import requests
from urllib.parse import quote

class SearchResult(BaseModel):
    id: str
    name: str

class PersonMetadata(BaseModel):
    name: str
    poster_url: Optional[str] = None

class Metadata(BaseModel):
    movie_title: Optional[str] = None
    genres: list[str] = []
    tags: list[str] = []
    collections: list[str] = []
    poster_url: Optional[str] = None
    people: list[PersonMetadata] = []

def search(title: str) -> list[SearchResult]:
    return findResults(search_name=title)

def findResults(search_name: str) -> list[SearchResult]:
    search_response = requests.get("https://scraper.url/search/" + quote(search_name))
    search_response.raise_for_status()
    #build search result for every response element and return them
    return []

def fetch_metadata(search_result: SearchResult, potential_collections: list[str]) -> Metadata:
    result = Metadata()
    detail_info_response = requests.get("https://scraper.url/details/" + search_result.id)
    detail_info_response.raise_for_status()
    #process data and add them to the result
    return result