def route_helper(route) -> dict:
    return {
        "id": str(route["_id"]),
        "routeName": route["routeName"],
        "active": route["active"],
        "createdAt": route["createdAt"].isoformat() if "createdAt" in route else None,
        
    }