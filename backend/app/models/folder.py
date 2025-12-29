from pydantic import BaseModel
from typing import List

class Folder(BaseModel):
    name: str
    path: str

class FolderListResponse(BaseModel):
    path: str
    entries: List[Folder]