from pydantic import BaseModel
from typing import Optional
from enum import StrEnum

class MOVIE_EXTRA_TYPE(StrEnum):
    BEHIND_THE_SCENES = 'BEHIND_THE_SCENES'
    MAKING_OFF = 'MAKING_OFF'
    TRAILER = 'TRAILER'

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
    is_extra_of_movie_id: Optional[int]
    extra_type: Optional[MOVIE_EXTRA_TYPE]

# Plex Extra Types
# -deleted
# -featurette
# -interview
# -scene
# -short
# -other