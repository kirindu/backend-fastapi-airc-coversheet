def load_helper(load) -> dict:
    """Helper para serializar documentos de load desde MongoDB"""
    return {
        "id": str(load["_id"]),
        "tunnelTimeInLoad": load.get("tunnelTimeInLoad", ""),
        "tunnelTimeOutLoad": load.get("tunnelTimeOutLoad", ""),
        "leaveYardLoad": load.get("leaveYardLoad", ""),
        "timeInLoad": load.get("timeInLoad", ""),
        "timeOutLoad": load.get("timeOutLoad", ""),
        "ticketNumberLoad": load.get("ticketNumberLoad", ""),
        "grossWeightLoad": load.get("grossWeightLoad", ""),
        "tareWeightLoad": load.get("tareWeightLoad", ""),
        "tonsLoad": load.get("tonsLoad", ""),
        "backYardLoad": load.get("backYardLoad", ""),
        "images": load.get("images", []),
        "image_path": load.get("image_path", None),
        "noteLoad": load.get("noteLoad", ""),
        "preloadedLoad": load.get("preloadedLoad", False),
        "preloadedNextDayLoad": load.get("preloadedNextDayLoad", False),
        
        # SINGLE RELATIONSHIPS - ✅ Convertir ObjectIds a strings
        "operator_id": str(load["operator_id"]) if load.get("operator_id") else None,
        "source_id": str(load["source_id"]) if load.get("source_id") else None,
        "destination_id": str(load["destination_id"]) if load.get("destination_id") else None,
        "material_id": str(load["material_id"]) if load.get("material_id") else None,
        
        # COVERSHEET REFERENCE - usar coversheet_ref_id en lugar de coversheet_id
        "coversheet_id": str(load["coversheet_ref_id"]) if load.get("coversheet_ref_id") else None,

        # EMBEDDED DATA (desnormalizado para performance)
        "operatorName": load.get("operatorName", ""),
        "sourceName": load.get("sourceName", ""),
        "destinationName": load.get("destinationName", ""),
        "materialName": load.get("materialName", ""),
        
        # AUDIT FIELDS  
        "createdAt": load["createdAt"].isoformat() if load.get("createdAt") else None,
        "updatedAt": load["updatedAt"].isoformat() if load.get("updatedAt") else None      
    }