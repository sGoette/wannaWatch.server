from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websocket_manager import ws_manager

import logging
log = logging.getLogger(__name__)

router = APIRouter(prefix="/ws")

@router.websocket("")
async def websocket(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(websocket)
