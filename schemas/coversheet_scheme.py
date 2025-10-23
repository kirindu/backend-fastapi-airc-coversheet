
def coversheet_helper(coversheet) -> dict:
    return {
        # TRUCK INFO
        "id": str(coversheet["_id"]),
        "clockIn": coversheet["clockIn"],
        "leaveYard": coversheet["leaveYard"],
        "backInYard": coversheet["backInYard"],
        "clockOut": coversheet["clockOut"],
        "startMiles": coversheet["startMiles"],
        "endMiles": coversheet["endMiles"],
        "fuel": coversheet["fuel"],
        
        # MULTIPLE RELATIONSHIPS (listas)
        "spareTruckInfo_id": coversheet.get("spareTruckInfo_id", []),
        "downtime_id": coversheet.get("downtime_id", []),
        "load_id": coversheet.get("load_id", []),
        
         # SINGLE RELATIONSHIPS
        "truck_id": coversheet["truck_id"],
        "route_id": coversheet["route_id"],
        "driver_id": coversheet["driver_id"],
        
        # Additional fields
        "truckNumber": coversheet.get("truckNumber", ""),
        "routeName": coversheet.get("routeName", ""),
        "driverName": coversheet.get("driverName", ""),
        
        # FIELDS
        "date": coversheet["date"].isoformat() if coversheet.get("date") else None,
        "notes": coversheet["notes"],
        "createdAt": coversheet["createdAt"].isoformat() if coversheet.get("createdAt") else None,
        "updatedAt": coversheet["updatedAt"].isoformat() if coversheet.get("updatedAt") else None
        
    }