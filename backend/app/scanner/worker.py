import asyncio
import threading
from app.scanner.jobs import ScanJob
from app.scanner.scan import scan_libraries

import logging
log = logging.getLogger(__name__)

from app.scanner.cleanup import cleanup_orphaned_posters, cleanup_orphaned_movies, cleanup_orphaned_collections

class ScannerWorker:
    def __init__(self):
        self.queue: asyncio.Queue[ScanJob] = asyncio.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.loop: asyncio.AbstractEventLoop | None = None

    def start(self):
        self.thread.start()

    def submit(self, job: ScanJob):
        if not self.loop:
            raise RuntimeError("Scanner worker not started")
        asyncio.run_coroutine_threadsafe(self.queue.put(job), self.loop)

    def _run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._worker_loop())

    async def _worker_loop(self):
        while True:
            job = await self.queue.get()
            try:
                # Scan all libraries for new movies
                await scan_libraries(job)

                #Cleanup orphaned movies in database -> Movies where the file is missing
                await cleanup_orphaned_movies()

                #Cleanup orphaned collections in database -> Collections with 0 movies
                await cleanup_orphaned_collections()
                
                #Cleanup orphaned posters after scanning
                await cleanup_orphaned_posters()
            except Exception:
                log.exception(f"Scanner Error: ")
            finally:
                self.queue.task_done()