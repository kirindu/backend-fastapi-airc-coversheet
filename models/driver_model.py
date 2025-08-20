from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime, timezone



class DriverModel(BaseModel):
    name: Optional[str]= None
    email: EmailStr
    rol: str = Field(default="Driver")
    password: str
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))