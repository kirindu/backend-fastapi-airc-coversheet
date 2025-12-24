def sparetruckinfo_helper(sparetruckinfo) -> dict:
    return {
        
        # GENERAL INFO
        "id": str(sparetruckinfo["_id"]),
        "timeLeaveYardSpareTruckInfo": sparetruckinfo["timeLeaveYardSpareTruckInfo"],
        "timeBackInYardSpareTruckInfo": sparetruckinfo["timeBackInYardSpareTruckInfo"],
        "fuelSpareTruckInfo": sparetruckinfo["fuelSpareTruckInfo"],
        "dieselExhaustFluidSpareTruckInfo": sparetruckinfo["dieselExhaustFluidSpareTruckInfo"],
        "truckStartMilesSpareTruckInfo": sparetruckinfo["truckStartMilesSpareTruckInfo"],
        "truckEndMilesSpareTruckInfo": sparetruckinfo["truckEndMilesSpareTruckInfo"], 
        "truckStartHoursSpareTruckInfo": sparetruckinfo["truckStartHoursSpareTruckInfo"],
        "truckEndHoursSpareTruckInfo": sparetruckinfo["truckEndHoursSpareTruckInfo"],
        "trailerStartMilesSpareTruckInfo": sparetruckinfo["trailerStartMilesSpareTruckInfo"],
        "trailerEndMilesSpareTruckInfo": sparetruckinfo["trailerEndMilesSpareTruckInfo"],
    
        # SINGLE RELATIONSHIPS - ✅ Convertir ObjectIds a strings
        "truck_id": str(sparetruckinfo["truck_id"]) if sparetruckinfo.get("truck_id") else None,
        "trailer_id": str(sparetruckinfo["trailer_id"]) if sparetruckinfo.get("trailer_id") else None,
        "coversheet_id": str(sparetruckinfo["coversheet_id"]) if sparetruckinfo.get("coversheet_id") else None,
        
        # Additional fields
        "truckNumber": sparetruckinfo.get("truckNumber", ""),
        "trailerNumber": sparetruckinfo.get("trailerNumber", ""),
        
        # AUDIT FIELDS
        "createdAt": sparetruckinfo["createdAt"].isoformat() if sparetruckinfo.get("createdAt") else None,
        "updatedAt": sparetruckinfo["updatedAt"].isoformat() if sparetruckinfo.get("updatedAt") else None
    }