import aiosqlite
from app.config import DB_PATH

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA journal_mode=WAL;")
    await db.execute("PRAGMA foreign_keys=ON;")
    return db

async def init_db():
    db = await get_db()

    await db.execute("PRAGMA foreign_keys=ON;")

    await db.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    format TEXT NOT NULL
)
""")
    await db.execute("""
INSERT INTO settings
( key, value, format )
VALUES
( 'MEDIA_ROOT_FOLDER', '', 'folder' )
ON CONFLICT(key) DO NOTHING
""")
    await db.execute("""
CREATE TABLE IF NOT EXISTS libraries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    media_folder TEXT NOT NULL UNIQUE
)
""")
    await db.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    file_location TEXT NOT NULL UNIQUE,
    length_in_seconds REAL,
    width INTEGER,
    height INTEGER,
    codec TEXT,
    format TEXT,
    poster_file_name TEXT,
    library_id INTEGER NOT NULL REFERENCES libraries(id) ON DELETE CASCADE
)
""")

    await db.execute("""
CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    poster_file_name TEXT,
    library_id INTEGER NOT NULL REFERENCES libraries(id) ON DELETE CASCADE
)
""")
    await db.execute("""
CREATE TABLE IF NOT EXISTS movies__collections (
    movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, collection_id)
)
""")
    await db.commit()
    await db.close()
