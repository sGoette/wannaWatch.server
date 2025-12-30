from fastapi import APIRouter, HTTPException, Query
from typing import List
from pathlib import Path
from app.config import DB_PATH
from app.models.folder import Folder, FolderListResponse
from app.config import GET_MEDIA_ROOT_FOLDER

router = APIRouter(prefix="/api/filesystem")

@router.get("/list", response_model=FolderListResponse)
async def get_folder_list(
    current_directory: str = Query("", description="Relative path inside media root")
):
    MEDIA_ROOT_FOLDER = Path(await GET_MEDIA_ROOT_FOLDER()).resolve()
    requested_path = (MEDIA_ROOT_FOLDER / current_directory)

    if not requested_path.is_relative_to(MEDIA_ROOT_FOLDER):
        raise HTTPException(status_code=400, detail="Invalid path")
    
    if not requested_path.exists() or not requested_path.is_dir():
        raise HTTPException(status_code=404, detail="Directory not found")
    
    directories: List[Folder] = []
    for entry in requested_path.iterdir():
        if entry.is_dir():
            directories.append(
                Folder(
                    name=entry.name, 
                    path=str(entry.relative_to(MEDIA_ROOT_FOLDER))
                )
            )

    return FolderListResponse(
        path=current_directory,
        entries=sorted(directories, key=lambda d: d.name.lower())
    )