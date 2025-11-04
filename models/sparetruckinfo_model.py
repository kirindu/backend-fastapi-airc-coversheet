from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime



class SpareTruckInfoModel(BaseModel):
    
    # GENERAL INFO
    timeLeaveYardSpareTruckInfo: str
    timeBackInYardSpareTruckInfo: str
    fuelSpareTruckInfo: str
    dieselExhaustFluidSpareTruckInfo: str
    
    spareTruckNumberSpareTruckInfo: Optional[str]= None
    truckStartMilesSpareTruckInfo: Optional[str]= None
    truckEndMilesSpareTruckInfo: Optional[str]= None
    truckStartHoursSpareTruckInfo: Optional[str]= None
    truckEndHoursSpareTruckInfo: Optional[str]= None
    
    spareTrailerNumberSpareTruckInfo: Optional[str]= None
    trailerStartMilesSpareTruckInfo: Optional[str]= None
    trailerEndMilesSpareTruckInfo: Optional[str]= None
    
    # RELATIONSHIP
    coversheet_id: Optional[str]= None
    
    
    # OTHER FIELDS
    homebase_id: str