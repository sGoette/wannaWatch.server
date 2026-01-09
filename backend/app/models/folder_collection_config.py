from pydantic import BaseModel
from typing import List
from pathlib import Path

class FolderCollectionConfig(BaseModel):
    subfoldersAreCollections: bool
    subfoldersAreCast: bool
    folderCast: List[str]

class FolderCollectionConfig_Path(BaseModel):
    data: FolderCollectionConfig
    path: Path