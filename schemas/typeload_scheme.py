
def typeload_helper(typeload) -> dict:
    return {
        "id": str(typeload["_id"]),
        "typeLoadName": typeload["typeLoadName"],
        "createdAt": typeload["createdAt"].isoformat() if "createdAt" in typeload else None,
        
    }