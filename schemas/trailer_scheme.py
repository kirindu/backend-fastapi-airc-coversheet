
def trailer_helper(trailer) -> dict:
    return {
        "id": str(trailer["_id"]),
        "trailerNumber": trailer["trailerNumber"],
        "createdAt": trailer["createdAt"].isoformat() if "createdAt" in trailer else None,
        
        
    
    }