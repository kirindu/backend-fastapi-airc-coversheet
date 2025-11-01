from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.typedowntime_model import TypeDownTimeModel
from config.database import typedowntimes_collection
from schemas.typedowntime_scheme import typedowntime_helper
from bson import ObjectId

router = APIRouter()

 
@router.post("/")
async def create_typedowntime(typedowntime: TypeDownTimeModel):
    try:
        new = await typedowntimes_collection.insert_one(typedowntime.model_dump())
        created = await typedowntimes_collection.find_one({"_id": new.inserted_id})
        return success_response(typedowntime_helper(created), msg="TypeDownTime creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el typedowntime: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_typedowntimes():
    try:
        typedowntimes = [typedowntime_helper(typedowntime) async for typedowntime in typedowntimes_collection.find().sort("typeDownTimeName", 1)]
        return success_response(typedowntimes, msg="Lista de typedowntimes obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los typedowntimes: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_typedowntime(id: str):
    typedowntime = await typedowntimes_collection.find_one({"_id": ObjectId(id)})
    if typedowntime:
        return success_response(typedowntime_helper(typedowntime), msg="TypeDownTime encontrado")
    return error_response("TypeDownTime no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_typedowntime(id: str, typedowntime: TypeDownTimeModel):
    res = await typedowntimes_collection.update_one({"_id": ObjectId(id)}, {"$set": typedowntime.model_dump()})
    if res.matched_count == 0:
        return error_response("TypeDownTime no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await typedowntimes_collection.find_one({"_id": ObjectId(id)})
    return success_response(typedowntime_helper(updated), msg="TypeDownTime actualizado")

@router.delete("/{id}")
async def delete_typedowntime(id: str):
    res = await typedowntimes_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="TypeDownTime eliminado")
    return error_response("TypeDownTime no encontrado", status_code=status.HTTP_404_NOT_FOUND)    