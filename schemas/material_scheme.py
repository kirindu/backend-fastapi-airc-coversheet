
def material_helper(material) -> dict:
    return {
        "id": str(material["_id"]),
        "materialName": material["materialName"],
        "createdAt": material["createdAt"].isoformat() if "createdAt" in material else None,
        
    }   