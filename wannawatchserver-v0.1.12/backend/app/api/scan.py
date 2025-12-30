from fastapi import APIRouter, Request
from app.scanner.jobs import ScanJob

router = APIRouter(prefix="/api/scan")

@router.post("/start")
async def start_scan(request: Request, library_id: int | None = None):
    scanner = request.app.state.scanner
    scanner.submit(ScanJob(library_id=library_id))
    return {"status": "scan queued"}