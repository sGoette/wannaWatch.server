from fastapi import APIRouter
import aiosqlite
from typing import List
from app.config import DB_PATH
from app.models.collection import CollectionWithStats, Collection

router = APIRouter(prefix="/api/collections")

@router.get("/{library_id}", response_model=List[CollectionWithStats])
async def get_collections(library_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
"""
SELECT c.*,
(
    SELECT COUNT(*)
    FROM movies__collections mc
    JOIN movies m ON mc.movie_id = m.id
    WHERE mc.collection_id = c.id
    AND m.is_extra_of_movie_id IS NULL
) movie_count
FROM collections c
WHERE library_id = ? 
ORDER BY c.title ASC
""", (library_id,)) as cursor: 
            rows = await cursor.fetchall()

        if rows is None:
            return []
        
        return [dict(row) for row in rows]