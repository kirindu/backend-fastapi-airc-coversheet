from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SpareTruckInfoModel(BaseModel):
    """Modelo base para SpareTruckInfo"""
    
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
    
    # RELATIONSHIPS
    truck_id: str
    trailer_id: str
    
    # AUDIT FIELDS (manejados automáticamente en el backend)
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class SpareTruckInfoCreateModel(SpareTruckInfoModel):
    """Modelo específico para CREAR sparetruckinfo - requiere coversheet_id"""
    coversheet_id: str  # OBLIGATORIO solo al crear


class SpareTruckInfoUpdateModel(BaseModel):
    """Modelo específico para ACTUALIZAR sparetruckinfo - todos los campos opcionales"""
    
    # GENERAL INFO
    timeLeaveYardSpareTruckInfo: Optional[str] = None
    timeBackInYardSpareTruckInfo: Optional[str] = None
    fuelSpareTruckInfo: Optional[str] = None
    dieselExhaustFluidSpareTruckInfo: Optional[str] = None
    truckStartMilesSpareTruckInfo: Optional[str] = None
    truckEndMilesSpareTruckInfo: Optional[str] = None
    truckStartHoursSpareTruckInfo: Optional[str] = None
    truckEndHoursSpareTruckInfo: Optional[str] = None
    trailerStartMilesSpareTruckInfo: Optional[str] = None
    trailerEndMilesSpareTruckInfo: Optional[str] = None
    
    # RELATIONSHIPS
    truck_id: Optional[str] = None
    trailer_id: Optional[str] = None
    
    # NO incluir coversheet_id aquí - no debe cambiar después de creación