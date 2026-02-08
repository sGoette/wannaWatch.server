from enum import StrEnum
from pydantic import BaseModel

class NOTIFICATION_TYPE(StrEnum):
    LIBRARIES_UPDATED = 'LIBRARIES_UPDATED'
    COLLECTIONS_UPDATED = 'COLLECTIONS_UPDATED'
    MOVIES_UPDATED = 'MOVIES_UPDATED'

class Notification(BaseModel):
    type: NOTIFICATION_TYPE