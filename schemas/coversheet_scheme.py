
def coversheet_helper(coversheet) -> dict:
    return {
        # GENERAL INFO
        "id": str(coversheet["_id"]),
        "clockIn": coversheet["clockIn"],
        "clockOut": coversheet["clockOut"],
        "trainee": coversheet["trainee"],
        "preTripStart": coversheet["preTripStart"],
        "preTripEnd": coversheet["preTripEnd"],
        "postTripStart": coversheet["postTripStart"],
        "postTripEnd": coversheet["postTripEnd"],
        "truckStartMiles": coversheet["truckStartMiles"],
        "truckEndMiles": coversheet["truckEndMiles"],
        "truckStartHours": coversheet["truckStartHours"],
        "truckEndHours": coversheet["truckEndHours"],
        "trailerStartMiles": coversheet["trailerStartMiles"],
        "trailerEndMiles": coversheet["trailerEndMiles"],
        "fuel": coversheet["fuel"],
        "dieselExhaustFluid": coversheet["dieselExhaustFluid"],

        "date": coversheet["date"].isoformat() if coversheet.get("date") else None,
        "notes": coversheet["notes"],
        
        # MULTIPLE RELATIONSHIPS (listas)
        "spareTruckInfo_id": coversheet.get("spareTruckInfo_id", []),
        "downtime_id": coversheet.get("downtime_id", []),
        "load_id": coversheet.get("load_id", []),
        
         # SINGLE RELATIONSHIPS
        "truck_id": coversheet["truck_id"],
        "trailer_id": coversheet["trailer_id"],
        "homebase_id": coversheet["homebase_id"],
        "driver_id": coversheet["driver_id"],
        
        # Additional fields
        "truckNumber": coversheet.get("truckNumber", ""),
        "trailerNumber": coversheet.get("trailerNumber", ""),
        "homeBaseName": coversheet.get("homeBaseName", ""),
        "driverName": coversheet.get("driverName", ""),
        
        # FIELDS

        "createdAt": coversheet["createdAt"].isoformat() if coversheet.get("createdAt") else None,
        "updatedAt": coversheet["updatedAt"].isoformat() if coversheet.get("updatedAt") else None
        
    }