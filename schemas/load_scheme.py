
def load_helper(load) -> dict:
    return {
        "id": str(load["_id"]),
        "tunnelTimeInLoad": load["tunnelTimeInLoad"],
        "tunnelTimeOutLoad": load["tunnelTimeOutLoad"],
        "leaveYardLoad": load["leaveYardLoad"],
        "timeInLoad": load["timeInLoad"],
        "timeOutLoad": load["timeOutLoad"],
        "ticketNumberLoad": load["ticketNumberLoad"],
        "grossWeightLoad": load["grossWeightLoad"],
        "tareWeightLoad": load["tareWeightLoad"],
        "tonsLoad": load["tonsLoad"],
        "backYardLoad": load["backYardLoad"],
        "images": load.get("images", []),
        "note": load["note"],
        "preloadedLoad": load.get("preloadedLoad", False),
        "preloadedNextDayLoad": load.get("preloadedNextDayLoad", False),
        
        
        # SINGLE RELATIONSHIPS
        "homebase_id": load.get("homebase_id", ""),
        "operator_id": load.get("operator_id", ""),
        "source_id": load.get("source_id", ""),
        "destination_id": load.get("destination_id", ""),
        "material_id": load.get("material_id", ""),

        # ADDITIONAL FIELDS
        "homeBaseName": load.get("homeBaseName", ""),
        "operatorName": load.get("operatorName", ""),
        "sourceName": load.get("sourceName", ""),
        "destinationName": load.get("destinationName", ""),
        "materialName": load.get("materialName", ""),
        
        # AUDIT FIELDS  
        "createdAt": load["createdAt"].isoformat() if load.get("createdAt") else None,
        "updatedAt": load["updatedAt"].isoformat() if load.get("updatedAt") else None      
    }   