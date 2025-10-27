
def operator_helper(operator) -> dict:
    return {
        "id": str(operator["_id"]),
        "operatorName": operator["operatorName"],
        "createdAt": operator["createdAt"].isoformat() if "createdAt" in operator else None,
        
    }