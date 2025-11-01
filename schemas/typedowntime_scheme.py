
def typedowntime_helper(typedowntime) -> dict:
    return {
        "id": str(typedowntime["_id"]),
        "typeDownTimeName": typedowntime["typeDownTimeName"],
        "createdAt": typedowntime["createdAt"].isoformat() if "createdAt" in typedowntime else None,
        
    }