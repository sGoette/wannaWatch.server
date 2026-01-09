from fastapi import APIRouter, HTTPException
import aiosqlite
from app.config import DB_PATH
from app.models.cast import Cast

router = APIRouter(prefix="/api/cast")

@router.get("/{cast_id}", response_model=Cast)
async def get_cast(cast_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM cast WHERE id = ?", (cast_id,)) as cursor:
            cast = await cursor.fetchone()

        if cast is None:
            raise HTTPException(status_code=404, detail="Cast not found")
        
        return dict(cast)