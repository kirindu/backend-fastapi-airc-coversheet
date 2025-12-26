from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DowntimeModel(BaseModel):
    """Modelo base para Downtime - usado en creación y actualización"""
    
    # GENERAL INFO
    truckDownTimeStartDownTime: str
    truckDownTimeEndDownTime: str
    trailerDownTimeStartDownTime: str
    trailerDownTimeEndDownTime: str
    downTimeReasonDownTime: str
    
    # RELATIONSHIPS
    truck_id: Optional[str] = None
    trailer_id: Optional[str] = None
    typeTruckDownTime_id: Optional[str] = None
    typeTrailerDownTime_id: Optional[str] = None
    
    # AUDIT FIELDS (manejados automáticamente en el backend)
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class DowntimeCreateModel(DowntimeModel):
    """Modelo específico para CREAR downtime - requiere coversheet_id"""
    coversheet_id: str  # OBLIGATORIO solo al crear


class DowntimeUpdateModel(BaseModel):
    """Modelo específico para ACTUALIZAR downtime - todos los campos opcionales"""
    
    # GENERAL INFO
    truckDownTimeStartDownTime: Optional[str] = None
    truckDownTimeEndDownTime: Optional[str] = None
    trailerDownTimeStartDownTime: Optional[str] = None
    trailerDownTimeEndDownTime: Optional[str] = None
    downTimeReasonDownTime: Optional[str] = None
    
    # RELATIONSHIPS
    truck_id: Optional[str] = None
    trailer_id: Optional[str] = None
    typeTruckDownTime_id: Optional[str] = None
    typeTrailerDownTime_id: Optional[str] = None
    
    # NO incluir coversheet_id aquí - no debe cambiar después de creación