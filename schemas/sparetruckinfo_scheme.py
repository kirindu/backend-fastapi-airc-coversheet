
def sparetruckinfo_helper(sparetruckinfo) -> dict:
    return {
        
        # GENERAL INFO
        
        "id": str(sparetruckinfo["_id"]),
        "timeLeaveYardSpareTruckInfo": sparetruckinfo["timeLeaveYardSpareTruckInfo"],
        "timeBackInYardSpareTruckInfo": sparetruckinfo["route_id"],
        "fuelSpareTruckInfo": sparetruckinfo["fuelSpareTruckInfo"],
        "dieselExhaustFluidSpareTruckInfo": sparetruckinfo["dieselExhaustFluidSpareTruckInfo"],
        
        "spareTruckNumberSpareTruckInfo": sparetruckinfo["spareTruckNumberSpareTruckInfo"],
        "truckStartMilesSpareTruckInfo": sparetruckinfo["truckStartMilesSpareTruckInfo"],
        "truckEndMilesSpareTruckInfo": sparetruckinfo["truckEndMilesSpareTruckInfo"], 
        "truckStartHoursSpareTruckInfo": sparetruckinfo["truckStartHoursSpareTruckInfo"],
        "truckEndHoursSpareTruckInfo": sparetruckinfo["truckEndHoursSpareTruckInfo"],
        
        
        "spareTrailerNumberSpareTruckInfo": sparetruckinfo["spareTrailerNumberSpareTruckInfo"],
        "trailerStartMilesSpareTruckInfo": sparetruckinfo["trailerStartMilesSpareTruckInfo"],
        "trailerEndMilesSpareTruckInfo": sparetruckinfo["trailerEndMilesSpareTruckInfo"],
    
    # SINGLE RELATIONSHIPS
    
        "homebase_id": sparetruckinfo["homebase_id"],
        "truck_id": sparetruckinfo["truck_id"],
        "trailer_id": sparetruckinfo["trailer_id"],
        
         # Additional fields
        "truckNumber": sparetruckinfo.get("truckNumber", ""),
        "trailerNumber": sparetruckinfo.get("trailerNumber", ""),
        "homeBaseName": sparetruckinfo.get("homeBaseName", ""),
        
              # AUDIT FIELDS

        "createdAt": sparetruckinfo["createdAt"].isoformat() if sparetruckinfo.get("createdAt") else None,
        "updatedAt": sparetruckinfo["updatedAt"].isoformat() if sparetruckinfo.get("updatedAt") else None
        
    
    }     