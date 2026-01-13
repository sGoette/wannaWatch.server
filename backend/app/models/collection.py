from pydantic import BaseModel
from typing import Optional

class Collection(BaseModel):
    id: int
    title: str
    poster_file_name: Optional[str]
    library_id: int