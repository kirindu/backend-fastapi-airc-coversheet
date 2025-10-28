from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.material_model import MaterialModel
from config.database import materials_collection
from schemas.material_scheme import material_helper
from bson import ObjectId

router = APIRouter()

 
@router.post("/")
async def create_material(material: MaterialModel):
    try:
        new = await materials_collection.insert_one(material.model_dump())
        created = await materials_collection.find_one({"_id": new.inserted_id})
        return success_response(material_helper(created), msg="Material creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el Material: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_materials():
    try:
        materials = [material_helper(material) async for material in materials_collection.find().sort("materialName", 1)]
        return success_response(materials, msg="Lista de material obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los materiales: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_material(id: str):
    material = await materials_collection.find_one({"_id": ObjectId(id)})
    if material:
        return success_response(material_helper(material), msg="Material encontrado")
    return error_response("Material no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_material(id: str, material: MaterialModel):
    res = await materials_collection.update_one({"_id": ObjectId(id)}, {"$set": material.model_dump()})
    if res.matched_count == 0:
        return error_response("Material no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await materials_collection.find_one({"_id": ObjectId(id)})
    return success_response(material_helper(updated), msg="Material actualizado")

@router.delete("/{id}")
async def delete_material(id: str):
    res = await materials_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="Material eliminado")
    return error_response("Material no encontrado", status_code=status.HTTP_404_NOT_FOUND)    