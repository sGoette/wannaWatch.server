from pydantic import BaseModel
from typing import Optional
from pathlib import Path

class Collection(BaseModel):
    id: int
    title: str
    poster_file_name: Optional[str]
    library_id: int

class CollectionData(BaseModel):
    title: str
    poster_file_name: Optional[str] = None
    poster_folder: Optional[Path] = None
    poster_url: Optional[str] = None

class CollectionWithStats(Collection):
    movie_count: int