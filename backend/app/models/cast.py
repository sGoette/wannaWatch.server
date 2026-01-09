from pydantic import BaseModel
from enum import StrEnum

class Role(StrEnum):
    ACTOR = 'ACTOR'
    DIRECTOR = 'DIRECTOR'


class Cast(BaseModel):
    id: int
    name: str
    poster_file_name: str
    role: Role