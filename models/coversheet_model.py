from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId


class CoversheetModel(BaseModel):
    # GENERAL INFO
    clockIn: str  
    clockOut: str  
    clockInTrainee: str  
    clockOutTrainee: str  
    trainee: str
    timePreTripStart: str
    timePreTripEnd: str
    timePostTripStart: str
    timePostTripEnd: str
    truckStartMiles: str
    truckEndMiles: str
    truckStartHours: str
    truckEndHours: str
    trailerStartMiles: str
    trailerEndMiles: str
    fuel: str
    dieselExhaustFluid: str
    
    date: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    notes: Optional[str] = None
    
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
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None
    
    