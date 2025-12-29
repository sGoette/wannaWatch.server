from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config import POSTER_DIR
from os import path

router = APIRouter(prefix="/api/poster")

@router.get("/{poster_file_name}")
async def get_poster(poster_file_name: str):
    file_path = path.join(POSTER_DIR, poster_file_name)
    
    if not path.exists(file_path):
        raise HTTPException(status_code=404, detail="Poster file not found on disk")
    
    return FileResponse(file_path)