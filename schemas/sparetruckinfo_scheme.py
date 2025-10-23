
def sparetruckinfo_helper(sparetruckinfo) -> dict:
    return {
        "id": str(sparetruckinfo["_id"]),
        "spareTruckNumber": sparetruckinfo["spareTruckNumber"],
        "route_id": sparetruckinfo["route_id"],
        "routeName": sparetruckinfo.get("routeName", ""),
        "leaveYard": sparetruckinfo["leaveYard"],
        "backInYard": sparetruckinfo["backInYard"],
        "startMiles": sparetruckinfo["startMiles"],
        "endMiles": sparetruckinfo["endMiles"],
        "fuel": sparetruckinfo["fuel"]
    }