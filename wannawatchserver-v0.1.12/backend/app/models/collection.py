from pydantic import BaseModel

class Collection(BaseModel):
    id: int
    title: str
    poster_file_name: str
    library_id: int