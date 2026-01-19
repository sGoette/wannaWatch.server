from fastapi import APIRouter, HTTPException
import aiosqlite

from app.config import DB_PATH
from app.models.person import Person

router = APIRouter(prefix="/api/person")

@router.get("/{person_id}", response_model=Person)
async def get_person(person_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM people WHERE id = ?", (person_id,)) as cursor:
            person = await cursor.fetchone()

        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        
        return dict(person)