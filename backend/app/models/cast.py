from pydantic import BaseModel
from enum import StrEnum

class Cast(BaseModel):
    id: int
    name: str
    poster_file_name: str
    role: Role

class Role(StrEnum):
    ACTOR = 'ACTOR'
    DIRECTOR = 'DIRECTOR'