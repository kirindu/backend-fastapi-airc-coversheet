
def coversheet_helper(coversheet) -> dict:
    return {
        # GENERAL INFO
        "id": str(coversheet["_id"]),
        "clockIn": coversheet["clockIn"],
        "clockOut": coversheet["clockOut"],
        "trainee": coversheet["trainee"],
        "clockInTrainee": coversheet["clockInTrainee"],
        "clockOutTrainee": coversheet["clockOutTrainee"],
        "timePreTripStart": coversheet["timePreTripStart"],
        "timePreTripEnd": coversheet["timePreTripEnd"],
        "timePostTripStart": coversheet["timePostTripStart"],
        "timePostTripEnd": coversheet["timePostTripEnd"],
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
        
     
# SINGLE RELATIONSHIPS (Asegúrate de que estos ahora se conviertan a str)
        "truck_id": str(coversheet["truck_id"]) if coversheet.get("truck_id") else None,
        "trailer_id": str(coversheet["trailer_id"]) if coversheet.get("trailer_id") else None,
        "homebase_id": str(coversheet["homebase_id"]) if coversheet.get("homebase_id") else None,
        "driver_id": str(coversheet["driver_id"]) if coversheet.get("driver_id") else None,
        
        # Additional fields
        "truckNumber": coversheet.get("truckNumber", ""),
        "trailerNumber": coversheet.get("trailerNumber", ""),
        "homeBaseName": coversheet.get("homeBaseName", ""),
        "driverName": coversheet.get("driverName", ""),
        
        # AUDIT FIELDS

        "createdAt": coversheet["createdAt"].isoformat() if coversheet.get("createdAt") else None,
        "updatedAt": coversheet["updatedAt"].isoformat() if coversheet.get("updatedAt") else None
        
    }