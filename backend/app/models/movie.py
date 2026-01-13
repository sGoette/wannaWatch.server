from pydantic import BaseModel
from typing import Optional

class Movie(BaseModel):
    id: int
    title: str
    file_location: str
    length_in_seconds: Optional[float]
    width: Optional[int]
    height: Optional[int]
    codec: Optional[str]
    format: Optional[str]
    poster_file_name: Optional[str]
    library_id: int
    metadata_last_updated: Optional[int]