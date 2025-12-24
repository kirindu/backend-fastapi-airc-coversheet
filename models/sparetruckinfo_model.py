from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SpareTruckInfoModel(BaseModel):
    
    # GENERAL INFO
    timeLeaveYardSpareTruckInfo: str
    timeBackInYardSpareTruckInfo: str
    fuelSpareTruckInfo: str
    dieselExhaustFluidSpareTruckInfo: str
    truckStartMilesSpareTruckInfo: str
    truckEndMilesSpareTruckInfo: str
    truckStartHoursSpareTruckInfo: str
    truckEndHoursSpareTruckInfo: str
    trailerStartMilesSpareTruckInfo: str
    trailerEndMilesSpareTruckInfo: str
    
    # RELATIONSHIPS
    truck_id: str
    trailer_id: str
    
    # coversheet_id es OBLIGATORIO al crear
    coversheet_id: str
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None