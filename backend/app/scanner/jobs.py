from dataclasses import dataclass
from typing import Optional

@dataclass
class ScanJob:
    library_id: Optional[int] = None
    ignore_existing_metadata: bool = False