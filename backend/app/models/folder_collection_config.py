from pydantic import BaseModel
from typing import List

class FolderCollectionConfig(BaseModel):
    subfoldersAreCollections: bool