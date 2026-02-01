from app.logging_setup import setup_logging
from app.config import LOG_FILE
setup_logging(log_path=LOG_FILE, level='WARNING')

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from zeroconf.asyncio import AsyncZeroconf

from app.api.health import router as health_router
from app.api.settings import router as settings_router
from app.api.movie import router as movie_router
from app.api.movies import router as movies_router
from app.api.collections import router as collections_router
from app.api.library import router as library_router
from app.api.libraries import router as libraries_router
from app.api.person import router as person_router
from app.api.poster import router as poster_router
from app.api.filesystem import router as filesystem_router
from app.api.scan import router as scan_router

from app.api.test import router as scrape_router

from app.db.database import init_db
from app.scanner.worker import ScannerWorker
from app.config import FRONTEND_DIR, INDEX_HTML

from app.services.bonjour import build_service_info

import logging
log = logging.getLogger(__name__)

LOG_FILE.write_text("")

scanner = ScannerWorker()

@asynccontextmanager
async def lifespan(api: FastAPI):
    # Startup
    await init_db()
    log.info("Database initialized ✅")

    scanner.start()
    app.state.scanner = scanner
    log.info("Scanner worker started ✅")

    zeroconf = AsyncZeroconf()
    info = await build_service_info()
    app.state.zeroconf = zeroconf
    app.state.service_info = info

    await zeroconf.async_register_service(info)
    
    yield

    await zeroconf.async_unregister_service(info)
    await zeroconf.async_close()

app = FastAPI(title="WannaWatch.server", lifespan=lifespan)

app.include_router(health_router)
app.include_router(settings_router)
app.include_router(movie_router)
app.include_router(movies_router)
app.include_router(collections_router)
app.include_router(library_router)
app.include_router(libraries_router)
app.include_router(person_router)
app.include_router(poster_router)
app.include_router(filesystem_router)
app.include_router(scan_router)

app.include_router(scrape_router)

if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

    # Serve SPA at "/"
    @app.get("/", include_in_schema=False)
    async def serve_index():
        if INDEX_HTML.exists():
            return FileResponse(INDEX_HTML)
        return {"detail": "Frontend not built (index.html missing)"}
    
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(request: Request, full_path: str):
        if request.url.path.startswith("/api/"):
            return {"detail": "Not Found"}
        
        candidate = (FRONTEND_DIR / full_path).resolve()
        try:
            candidate.relative_to(FRONTEND_DIR.resolve())
            if candidate.exists() and candidate.is_file():
                return FileResponse(candidate)
        except Exception:
            log.exception("Can not get frontend file {candidate}")
            pass

        if INDEX_HTML.exists():
            return FileResponse(INDEX_HTML)
        return {"detail": "Frontend not built (index.html missing)"}
    