from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class DestinationModel(BaseModel):
    destinationName: str
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))