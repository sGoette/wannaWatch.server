from pydantic import BaseModel
from typing import Optional

class Setting(BaseModel):
    key: str
    value: Optional[str]
    format: Optional[str]