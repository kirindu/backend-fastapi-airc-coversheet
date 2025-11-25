from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class OperatorModel(BaseModel):
    operatorName: str
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    