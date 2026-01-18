from pydantic import BaseModel
from enum import StrEnum
from typing import Optional

class ROLE(StrEnum):
    ACTOR = 'ACTOR'
    DIRECTOR = 'DIRECTOR'


class Cast(BaseModel):
    id: int
    name: str
    poster_file_name: Optional[str]
    role: ROLE