from pydantic import BaseModel
from typing import Optional

class Library(BaseModel):
    id: int
    name: Optional[str]
    media_folder: str

class LibraryCreate(BaseModel):
    name: str
    media_folder: str