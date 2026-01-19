from pydantic import BaseModel
from typing import Optional

from app.models.collection import CollectionData

class PersonMetadata(BaseModel):
    name: str
    poster_url: Optional[str] = None
    
class Metadata(BaseModel):
    movie_title: Optional[str] = None
    genres: list[str] = []
    tags: list[str] = []
    collections: list[CollectionData] = []
    poster_url: Optional[str] = None
    people: list[PersonMetadata] = []

class SearchResult(BaseModel):
    id: str
    name: str