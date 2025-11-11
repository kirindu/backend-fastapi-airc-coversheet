from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
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
    
    # RELATIONSHIP
    coversheet_id: Optional[str]= None # Esto se hace opcional porque a la hora actualizar el spare no se necesita este campo.
    
    
    # ANOTHER RELATIONSHIPS
    homebase_id: str
    truck_id: str
    trailer_id: str
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None