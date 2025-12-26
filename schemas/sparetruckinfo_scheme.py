def sparetruckinfo_helper(sparetruckinfo) -> dict:
    """Helper para serializar documentos de sparetruckinfo desde MongoDB"""
    return {
        # GENERAL INFO
        "id": str(sparetruckinfo["_id"]),
        "timeLeaveYardSpareTruckInfo": sparetruckinfo.get("timeLeaveYardSpareTruckInfo", ""),
        "timeBackInYardSpareTruckInfo": sparetruckinfo.get("timeBackInYardSpareTruckInfo", ""),
        "fuelSpareTruckInfo": sparetruckinfo.get("fuelSpareTruckInfo", ""),
        "dieselExhaustFluidSpareTruckInfo": sparetruckinfo.get("dieselExhaustFluidSpareTruckInfo", ""),
        "truckStartMilesSpareTruckInfo": sparetruckinfo.get("truckStartMilesSpareTruckInfo", ""),
        "truckEndMilesSpareTruckInfo": sparetruckinfo.get("truckEndMilesSpareTruckInfo", ""), 
        "truckStartHoursSpareTruckInfo": sparetruckinfo.get("truckStartHoursSpareTruckInfo", ""),
        "truckEndHoursSpareTruckInfo": sparetruckinfo.get("truckEndHoursSpareTruckInfo", ""),
        "trailerStartMilesSpareTruckInfo": sparetruckinfo.get("trailerStartMilesSpareTruckInfo", ""),
        "trailerEndMilesSpareTruckInfo": sparetruckinfo.get("trailerEndMilesSpareTruckInfo", ""),
    
        # SINGLE RELATIONSHIPS - ✅ Convertir ObjectIds a strings
        "truck_id": str(sparetruckinfo["truck_id"]) if sparetruckinfo.get("truck_id") else None,
        "trailer_id": str(sparetruckinfo["trailer_id"]) if sparetruckinfo.get("trailer_id") else None,
        
        # COVERSHEET REFERENCE - usar coversheet_ref_id en lugar de coversheet_id
        "coversheet_id": str(sparetruckinfo["coversheet_ref_id"]) if sparetruckinfo.get("coversheet_ref_id") else None,
        
        # EMBEDDED DATA (desnormalizado para performance)
        "truckNumber": sparetruckinfo.get("truckNumber", ""),
        "trailerNumber": sparetruckinfo.get("trailerNumber", ""),
        
        # AUDIT FIELDS
        "createdAt": sparetruckinfo["createdAt"].isoformat() if sparetruckinfo.get("createdAt") else None,
        "updatedAt": sparetruckinfo["updatedAt"].isoformat() if sparetruckinfo.get("updatedAt") else None
    }