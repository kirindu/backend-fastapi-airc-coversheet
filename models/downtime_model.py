from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
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