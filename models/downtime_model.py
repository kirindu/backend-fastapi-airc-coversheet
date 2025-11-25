from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from datetime import datetime

class DowntimeModel(BaseModel):
    
    # GENERAL INFO
    truckDownTimeStartDownTime: str
    truckDownTimeEndDownTime: str
    trailerDownTimeStartDownTime: str
    trailerDownTimeEndDownTime: str
    
    downTimeReasonDownTime: str
    
       # RELATIONSHIP
    coversheet_id: Optional[str]= None # Esto se hace opcional porque a la hora actualizar el downtime no se necesita este campo.
    
        # ANOTHER RELATIONSHIPS
    truck_id: Optional[str]= None
    trailer_id: Optional[str]= None
 
    typeTruckDownTime_id: Optional[str]= None
    typeTrailerDownTime_id: Optional[str]= None
    
        # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None