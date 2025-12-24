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
        "image_path": load.get("image_path", None),
        "noteLoad": load["noteLoad"],
        "preloadedLoad": load.get("preloadedLoad", False),
        "preloadedNextDayLoad": load.get("preloadedNextDayLoad", False),
        
        
        # SINGLE RELATIONSHIPS - ✅ Convertir ObjectIds a strings
        "operator_id": str(load["operator_id"]) if load.get("operator_id") else None,
        "source_id": str(load["source_id"]) if load.get("source_id") else None,
        "destination_id": str(load["destination_id"]) if load.get("destination_id") else None,
        "material_id": str(load["material_id"]) if load.get("material_id") else None,
        "coversheet_id": str(load["coversheet_id"]) if load.get("coversheet_id") else None,

        # ADDITIONAL FIELDS
        "operatorName": load.get("operatorName", ""),
        "sourceName": load.get("sourceName", ""),
        "destinationName": load.get("destinationName", ""),
        "materialName": load.get("materialName", ""),
        
        # AUDIT FIELDS  
        "createdAt": load["createdAt"].isoformat() if load.get("createdAt") else None,
        "updatedAt": load["updatedAt"].isoformat() if load.get("updatedAt") else None      
    }