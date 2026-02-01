import aiosqlite
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve() #wannawatch.server folder
POSTER_DIR = BASE_DIR / "data/posters"
DB_PATH = BASE_DIR / "data/db/database.sqlite"

BACKEND_DIR = Path(__file__).resolve().parents[1]      # backend/app -> backend
REPO_ROOT   = BACKEND_DIR.parent                       # backend -> repo root
LOG_FILE     = BASE_DIR / "data/wannawatch.log"

FRONTEND_DIR = REPO_ROOT / "frontend"                  # repo_root/frontend
INDEX_HTML = FRONTEND_DIR / "index.html"

async def GET_MEDIA_ROOT_FOLDER() -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT value FROM settings WHERE key = 'MEDIA_ROOT_FOLDER'") as cursor:
            MEDIA_ROOT_FOLDER = await cursor.fetchone()

        if MEDIA_ROOT_FOLDER:
            return str(MEDIA_ROOT_FOLDER[0])
        
        exit(1)

async def GET_SERVER_NAME() -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT value FROM settings WHERE key = 'SERVER_NAME'") as cursor:
            SERVER_NAME = await cursor.fetchone()

            if SERVER_NAME:
                return str(SERVER_NAME[0])
            
            exit(1)

COLLECTION_POSTER_CANDIDATE_NAMES = ['folder' 'cover', 'poster', 'thumb', 'thumbnail', 'collection']

VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'}