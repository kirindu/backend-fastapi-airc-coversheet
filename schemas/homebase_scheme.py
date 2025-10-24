
def homebase_helper(homebase) -> dict:
    return {
        "id": str(homebase["_id"]),
        "homeBaseName": homebase["homeBaseName"],
        "createdAt": homebase["createdAt"].isoformat() if "createdAt" in homebase else None,
        
    }