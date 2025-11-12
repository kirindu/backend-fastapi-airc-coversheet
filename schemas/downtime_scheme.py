
def downtime_helper(downtime) -> dict:
    return {
        "id": str(downtime["_id"]),
        "truckDownTimeStartDownTime": downtime["truckDownTimeStartDownTime"],
        "truckDownTimeEndDownTime": downtime["truckDownTimeEndDownTime"],
        "trailerDownTimeStartDownTime": downtime["trailerDownTimeStartDownTime"],
        "trailerDownTimeEndDownTime": downtime["trailerDownTimeEndDownTime"],
        "downTimeReasonDownTime": downtime["downTimeReasonDownTime"],
        
         # SINGLE RELATIONSHIPS
         
        "truck_id": downtime.get("truck_id", ""),
        "trailer_id": downtime.get("trailer_id", ""),
        "typeTruckDownTime_id": downtime.get("typeTruckDownTime_id", ""),
        "typeTrailerDownTime_id": downtime.get("typeTrailerDownTime_id", ""),
        
        # Additional fields
        
        "truckNumber": downtime.get("truckNumber", ""),
        "trailerNumber": downtime.get("trailerNumber", ""),
        "typeTruckDownTimeName": downtime.get("typeTruckDownTimeName", ""),
        "typeTrailerDownTimeName": downtime.get("typeTrailerDownTimeName", ""),
        
        # AUDIT FIELDS
        
        "createdAt": downtime["createdAt"].isoformat() if downtime.get("createdAt") else None,
        "updatedAt": downtime["updatedAt"].isoformat() if downtime.get("updatedAt") else None   
         
         
    }