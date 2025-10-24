
def homebase_helper(homebase) -> dict:
    return {
        "id": str(homebase["_id"]),
        "homeBaseNumber": homebase["homeBaseNumber"],
        "createdAt": homebase["createdAt"].isoformat() if "createdAt" in homebase else None,
        
    }