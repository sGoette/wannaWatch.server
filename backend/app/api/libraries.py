from fastapi import APIRouter
from typing import List
import aiosqlite
from app.config import DB_PATH
from app.models.library import Library

router = APIRouter(prefix="/api/libraries")

@router.get("", response_model=List[Library])
async def get_libraries():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM libraries ORDER BY name ASC")
        rows = await cursor.fetchall()

    if not rows:
        # Return empty array instead of 404
        return []
    
    #Convert each row to dict
    return [dict(row) for row in rows]