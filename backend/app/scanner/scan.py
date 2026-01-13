import aiosqlite

from app.config import DB_PATH
from app.scanner.jobs import ScanJob
from app.models.library import Library
from app.scanner.library import scan_library


async def scan_libraries(job: ScanJob):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")

        if job.library_id:
            cursor = await db.execute("SELECT * FROM libraries WHERE id = ?", (job.library_id,))
        else: 
            cursor = await db.execute("SELECT * FROM libraries")

        rows = await cursor.fetchall()
        await cursor.close()

        libraries = [Library(**dict(row)) for row in rows]

        for library in libraries:
            await scan_library(library)


