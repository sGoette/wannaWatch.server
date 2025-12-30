from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import aiosqlite
from os import path
from app.config import DB_PATH
from app.models.movie import Movie
from app.config import GET_MEDIA_ROOT_FOLDER

router = APIRouter(prefix="/api/movie")

@router.get("/{movie_id}", response_model=Movie)
async def get_movie(movie_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)) as cursor:
            movie = await cursor.fetchone()

    if movie is None: 
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return movie

CHUNK_SIZE = 1024 * 1024  # 1MB per chunk

@router.get("/{movie_id}/stream")
async def stream_movie(request: Request, movie_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)) as cursor:
            movie = await cursor.fetchone()
        MEDIA_ROOT_FOLDER = await GET_MEDIA_ROOT_FOLDER()

    if not movie or not MEDIA_ROOT_FOLDER:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    file_path = path.join(MEDIA_ROOT_FOLDER, movie["file_location"])
    if not path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    file_size = path.getsize(file_path)
    headers = { "Accept-Ranges": "bytes" }

    range_header = request.headers.get("range")
    if range_header:
        bytes_range = range_header.strip().split("=")[-1]
        start_str, end_str = bytes_range.split("-")
        start = int(start_str)
        end = int(end_str) if end_str else file_size - 1
        length = end - start + 1

        def iter_file():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk_size = min(CHUNK_SIZE, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    yield data
                    remaining -= len(data)

        headers.update({
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Content-Length": str(length)
        })
        return StreamingResponse(iter_file(), status_code=206, headers=headers, media_type="video/mp4")
    
    else:
        # No Range header, return entire file
        def iter_file_full():
            with open(file_path, "rb") as f:
                while True:
                    data = f.read(CHUNK_SIZE)
                    if not data:
                        break
                    yield data

        headers.update({ "Content-Length": str(file_size) })
        return StreamingResponse(iter_file_full(), headers=headers, media_type="video/mp4")