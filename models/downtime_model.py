from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DowntimeModel(BaseModel):
    
    # GENERAL INFO
    truckDownTimeStartDownTime: str
    truckDownTimeEndDownTime: str
    trailerDownTimeStartDownTime: str
    trailerDownTimeEndDownTime: str
    downTimeReasonDownTime: str
    
    # RELATIONSHIPS
    truck_id: Optional[str] = None
    trailer_id: Optional[str] = None
    typeTruckDownTime_id: Optional[str] = None
    typeTrailerDownTime_id: Optional[str] = None
    
    # coversheet_id es OBLIGATORIO al crear
    coversheet_id: str
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None