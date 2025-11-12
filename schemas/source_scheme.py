
def source_helper(source) -> dict:
    return {
        "id": str(source["_id"]),
        "sourceName": source["sourceName"],
        "createdAt": source["createdAt"].isoformat() if "createdAt" in source else None,
        
    }   