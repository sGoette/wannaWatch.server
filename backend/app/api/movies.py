from fastapi import APIRouter
from typing import List
import aiosqlite
from app.config import DB_PATH
from app.models.movie import Movie

router = APIRouter(prefix="/api/movies")

@router.get("/{library_id}", response_model=List[Movie])
async def get_movies(library_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE is_extra_of_movie_id IS NULL AND library_id = ? ORDER BY title ASC", (library_id,)) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        # Return empty array instead of 404
        return []
    
    #Convert each row to dict
    return [dict(row) for row in rows]

@router.get("/collection/{collection_id}", response_model=List[Movie])
async def get_movies_of_collection(collection_id):
    async with aiosqlite.connect(DB_PATH) as db: 
        db.row_factory = aiosqlite.Row
        async with db.execute("""
SELECT m.*
FROM movies m
JOIN movies__collections mc ON mc.movie_id = m.id
WHERE mc.collection_id = ?
AND m.is_extra_of_movie_id IS NULL
ORDER BY m.title ASC
""", (collection_id,)) as cursor:
            rows = await cursor.fetchall()

    if not rows:
        return []

    return [dict(row) for row in rows]    
