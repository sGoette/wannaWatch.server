import asyncio
import threading
from app.scanner.jobs import ScanJob
from app.scanner.scan import scan_libraries
import traceback

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
                await scan_libraries(job)
            except Exception as e:
                print(f"[Scanner] Error: {e}")
                traceback.print_exc()
            finally:
                self.queue.task_done()