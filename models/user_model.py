
from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId



class UserModel(BaseModel):
    name: str
    email: EmailStr
    rol: str
    password: str
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))