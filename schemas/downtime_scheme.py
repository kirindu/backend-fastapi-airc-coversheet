def downtime_helper(downtime) -> dict:
    """Helper para serializar documentos de downtime desde MongoDB"""
    return {
        "id": str(downtime["_id"]),
        
        # GENERAL INFO
        "truckDownTimeStartDownTime": downtime.get("truckDownTimeStartDownTime", ""),
        "truckDownTimeEndDownTime": downtime.get("truckDownTimeEndDownTime", ""),
        "trailerDownTimeStartDownTime": downtime.get("trailerDownTimeStartDownTime", ""),
        "trailerDownTimeEndDownTime": downtime.get("trailerDownTimeEndDownTime", ""),
        "downTimeReasonDownTime": downtime.get("downTimeReasonDownTime", ""),
        
        # SINGLE RELATIONSHIPS - ✅ Convertir ObjectIds a strings
        "truck_id": str(downtime["truck_id"]) if downtime.get("truck_id") else None,
        "trailer_id": str(downtime["trailer_id"]) if downtime.get("trailer_id") else None,
        "typeTruckDownTime_id": str(downtime["typeTruckDownTime_id"]) if downtime.get("typeTruckDownTime_id") else None,
        "typeTrailerDownTime_id": str(downtime["typeTrailerDownTime_id"]) if downtime.get("typeTrailerDownTime_id") else None,
        
        # COVERSHEET REFERENCE - usar coversheet_ref_id en lugar de coversheet_id
        "coversheet_id": str(downtime["coversheet_ref_id"]) if downtime.get("coversheet_ref_id") else None,
        
        # EMBEDDED DATA (desnormalizado para performance)
        "truckNumber": downtime.get("truckNumber", ""),
        "trailerNumber": downtime.get("trailerNumber", ""),
        "typeTruckDownTimeName": downtime.get("typeTruckDownTimeName", ""),
        "typeTrailerDownTimeName": downtime.get("typeTrailerDownTimeName", ""),
        
        # AUDIT FIELDS
        "createdAt": downtime["createdAt"].isoformat() if downtime.get("createdAt") else None,
        "updatedAt": downtime["updatedAt"].isoformat() if downtime.get("updatedAt") else None   
    }