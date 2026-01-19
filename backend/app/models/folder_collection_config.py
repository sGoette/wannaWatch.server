from pydantic import BaseModel
from pathlib import Path
from typing import Optional

class FolderCollectionConfig(BaseModel):
    subfoldersAreCollections: bool
    subfoldersArePeople: bool
    folderPeople: list[str]
    useScraper: bool
    potential_collections: list[str]


class FolderCollectionConfig_Path(BaseModel):
    data: FolderCollectionConfig
    currentPath: Path
    childPath: Optional[Path]