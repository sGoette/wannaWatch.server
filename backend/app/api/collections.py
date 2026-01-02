from fastapi import APIRouter
import aiosqlite
from typing import List
from app.config import DB_PATH
from app.models.collection import Collection

router = APIRouter(prefix="/api/collections")

@router.get("/{library_id}", response_model=List[Collection])
async def get_collections(library_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM collections WHERE library_id = ? ORDER BY title ASC", (library_id,)) as cursor: 
            rows = await cursor.fetchall()

        if rows is None:
            return []
        
        return [dict(row) for row in rows]