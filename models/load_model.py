from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from datetime import datetime

class LoadModel(BaseModel):
    
    
    # GENERAL INFO
    tunnelTimeInLoad: str
    tunnelTimeOutLoad: str
    leaveYardLoad: str
    timeInLoad: str
    timeOutLoad: str
    ticketNumberLoad: str
    grossWeightLoad: str
    tareWeightLoad: str
    tonsLoad: str
    backYardLoad: str
    noteLoad: Optional[str]= None
    preloadedLoad: Optional[bool]= False
    preloadedNextDayLoad: Optional[bool]= False
    images: Optional[list]= []
    image_path: Optional[str]= None
    
    
    # RELATIONSHIP
    coversheet_id: Optional[str]= None # Esto se hace opcional porque a la hora actualizar el spare no se necesita este campo.
    
    
     # ANOTHER RELATIONSHIPS
    # homebase_id: Optional[str]= None
    operator_id: Optional[str]= None
    source_id: Optional[str]= None
    destination_id: Optional[str]= None
    material_id: Optional[str]= None
    coversheet_id: Optional[str]= None
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None
 