
def destination_helper(destination) -> dict:
    return {
        "id": str(destination["_id"]),
        "destinationName": destination["destinationName"],
        "createdAt": destination["createdAt"].isoformat() if "createdAt" in destination else None,
        
    }   