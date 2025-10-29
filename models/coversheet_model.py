from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId


class CoversheetModel(BaseModel):
    # TRUCK INFO
    clockIn: str  
    leaveYard: str  
    backInYard: str  
    clockOut: str  
    startMiles: str
    endMiles: str
    fuel: str
    
    dieselExhaustFluid: str
    helper: str
    
    
    
    # SPARE TRUCK INFO -RELATIONSHIP
    spareTruckInfo_id: Optional[List[str]] = []
    
    # DOWNTIME - RELATIONSHIP
    downtime_id: Optional[List[str]] = []
    
    # LOAD - RELATIONSHIP
    load_id: Optional[List[str]] = []
    
    # ANOTHER RELATIONSHIPS
    
    homebase_id: str
    truck_id: str
    trailer_id: str
    
    driver_id: str
    
    # FIELDS
    date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None
    
    