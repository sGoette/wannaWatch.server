from fastapi import APIRouter, HTTPException, Request
import aiosqlite
from app.scanner.jobs import ScanJob
from app.config import DB_PATH
from app.models.library import Library, LibraryCreate

router = APIRouter(prefix="/api/library")

@router.get("/{library_id}", response_model=Library)
async def get_library(library_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM libraries WHERE id = ?", (library_id,))
        library = await cursor.fetchone()
        await cursor.close()

    if library is None:
        raise HTTPException(status_code=404, detail="Library not found")

    return dict(library)

@router.put("", response_model=Library)
async def create_library(request: Request, library: LibraryCreate):
    async with aiosqlite.connect(DB_PATH) as db:
        # TODO: Handle ON CONFLICT. Idealy with a response so the user knows the media_library already exists
        cursor = await db.execute("INSERT INTO libraries (name, media_folder) VALUES (?, ?)", (library.name, library.media_folder))
        await db.commit()
        library_id = cursor.lastrowid
        await cursor.close()

    scanner = request.app.state.scanner
    scanner.submit(ScanJob(library_id=library_id))
    # Return the created library
    if library_id:
        return Library(
            id=library_id,
            name=library.name,
            media_folder=library.media_folder
        )
    
@router.post("", response_model=Library)
async def update_library(library: Library):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE libraries SET name = ?, media_folder = ? WHERE id = ?", (library.name, library.media_folder, library.id))
        await db.commit()
        await db.close()

    #Return the updated library
    return library

@router.delete("/{library_id}")
async def delete_library(request: Request,library_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # TODO: Delete all thumbnails before deleting the movies and collections!
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute("DELETE FROM libraries WHERE id = ?", (library_id,))
        await db.commit()
        rowcount = cursor.rowcount
        await db.close()

    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Library not found")
    
    scanner = request.app.state.scanner
    scanner.submit(ScanJob(library_id=library_id))
    
    return {"msg": "Library deleted"}