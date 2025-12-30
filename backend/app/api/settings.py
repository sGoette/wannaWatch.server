from fastapi import APIRouter
from typing import List
import aiosqlite
from app.config import DB_PATH
from app.models.setting import Setting

router = APIRouter(prefix="/api/settings")

@router.get("", response_model=List[Setting])
async def get_settings():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM settings ORDER BY key ASC")
        rows = await cursor.fetchall()
        await cursor.close()

    #Convert each row to dict
    return [dict(row) for row in rows]

@router.post("")
async def post_settings(settings: List[Setting]):
    async with aiosqlite.connect(DB_PATH) as db:
        for setting in settings:
            # TODO: Check if libraries exist. If yes, they have to be deleted with all their files. 
            await db.execute("UPDATE settings SET value = ? WHERE key = ?", (setting.value, setting.key))
            await db.commit()
            await db.close()

    return {"detail": "Settings updated successfully"}