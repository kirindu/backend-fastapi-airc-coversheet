from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId


class CoversheetModel(BaseModel):
    # GENERAL INFO
    clockIn: str  
    clockOut: str  
    trainee: str
    preTripStart: str
    preTripEnd: str
    postTripStart: str
    postTripEnd: str
    truckStartMiles: str
    truckEndMiles: str
    truckStartHours: str
    truckEndHours: str
    trailerStartMiles: str
    trailerEndMiles: str
    fuel: str
    dieselExhaustFluid: str
    
    date: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
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
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = None
    
    