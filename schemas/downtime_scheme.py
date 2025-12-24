def downtime_helper(downtime) -> dict:
    return {
        "id": str(downtime["_id"]),
        "truckDownTimeStartDownTime": downtime["truckDownTimeStartDownTime"],
        "truckDownTimeEndDownTime": downtime["truckDownTimeEndDownTime"],
        "trailerDownTimeStartDownTime": downtime["trailerDownTimeStartDownTime"],
        "trailerDownTimeEndDownTime": downtime["trailerDownTimeEndDownTime"],
        "downTimeReasonDownTime": downtime["downTimeReasonDownTime"],
        
        # SINGLE RELATIONSHIPS - ✅ Convertir ObjectIds a strings
        "truck_id": str(downtime["truck_id"]) if downtime.get("truck_id") else None,
        "trailer_id": str(downtime["trailer_id"]) if downtime.get("trailer_id") else None,
        "typeTruckDownTime_id": str(downtime["typeTruckDownTime_id"]) if downtime.get("typeTruckDownTime_id") else None,
        "typeTrailerDownTime_id": str(downtime["typeTrailerDownTime_id"]) if downtime.get("typeTrailerDownTime_id") else None,
        "coversheet_id": str(downtime["coversheet_id"]) if downtime.get("coversheet_id") else None,
        
        # ADDITIONAL FIELDS
        "truckNumber": downtime.get("truckNumber", ""),
        "trailerNumber": downtime.get("trailerNumber", ""),
        "typeTruckDownTimeName": downtime.get("typeTruckDownTimeName", ""),
        "typeTrailerDownTimeName": downtime.get("typeTrailerDownTimeName", ""),
        
        # AUDIT FIELDS
        "createdAt": downtime["createdAt"].isoformat() if downtime.get("createdAt") else None,
        "updatedAt": downtime["updatedAt"].isoformat() if downtime.get("updatedAt") else None   
    }
