import asyncio
from typing import Set
from fastapi import WebSocket
from app.models.notification import Notification
import base64

import logging
log = logging.getLogger(__name__)

class WSManager:
    def __init__(self) -> None:
        self._clients: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._clients.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def broadcast(self, message: Notification) -> None:
        async with self._lock:
            clients = list(self._clients)

        dead: list[WebSocket] = []
        for client in clients:
            try:
                await client.send_text(message.model_dump_json())
            except Exception:
                log.exception("Unable to send data")
                dead.append(client)

        if dead:
            async with self._lock:
                for client in dead:
                    self._clients.discard(client)

ws_manager = WSManager()
