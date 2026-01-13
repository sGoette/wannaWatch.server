import json as jsone
from pathlib import Path

from app.config import GET_MEDIA_ROOT_FOLDER
from app.models.folder_collection_config import FolderCollectionConfig, FolderCollectionConfig_Path


async def find_folder_collection_config(start_path: Path) -> list[FolderCollectionConfig_Path]:
    MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()
    current = start_path.parent if start_path.is_file() else start_path
    last_folder = None
    configs: list[FolderCollectionConfig_Path] = []

    while True:
        candidate = current / '__wannawatch.json'
        if candidate.is_file():
            with candidate.open("r", encoding="utf-8") as f:
                data = jsone.load(f)
                entry = FolderCollectionConfig_Path(data=FolderCollectionConfig(**data), currentPath=current, childPath=last_folder) #TODO: compare lowercase with lowercase
                configs.append(entry)
        
        if current == MEDIA_ROOT_FOLDER:
            break
        if current.parent == current:
            break

        last_folder = current
        current = current.parent
        
    return configs