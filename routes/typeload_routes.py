from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.typeload_model import TypeLoadModel
from config.database import typeloads_collection
from schemas.typeload_scheme import typeload_helper
from bson import ObjectId

router = APIRouter()

 
@router.post("/")
async def create_typeload(typeload: TypeLoadModel):
    try:
        new = await typeloads_collection.insert_one(typeload.model_dump())
        created = await typeloads_collection.find_one({"_id": new.inserted_id})
        return success_response(typeload_helper(created), msg="Typeloads creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el typeload: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_typeloads():
    try:
        typeloads = [typeload_helper(typeload) async for typeload in typeloads_collection.find().sort("typeLoadName", 1)]
        return success_response(typeloads, msg="Lista de typeloads obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los typeloads: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_typeload(id: str):
    typeload = await typeloads_collection.find_one({"_id": ObjectId(id)})
    if typeload:
        return success_response(typeload_helper(typeload), msg="TypeLoad encontrado")
    return error_response("TypeLoad no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_typeload(id: str, typeload: TypeLoadModel):
    res = await typeloads_collection.update_one({"_id": ObjectId(id)}, {"$set": typeload.model_dump()})
    if res.matched_count == 0:
        return error_response("TypeLoad no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await typeloads_collection.find_one({"_id": ObjectId(id)})
    return success_response(typeload_helper(updated), msg="TypeLoad actualizado")

@router.delete("/{id}")
async def delete_typeload(id: str):
    res = await typeloads_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="TypeLoad eliminado")
    return error_response("TyleLoad no encontrado", status_code=status.HTTP_404_NOT_FOUND)    