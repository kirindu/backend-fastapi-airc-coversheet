from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.homebase_model import HomeBaseModel
from config.database import homebases_collection
from schemas.homebase_scheme import homebase_helper
from bson import ObjectId

router = APIRouter()

 
@router.post("/")
async def create_homebase(homebase: HomeBaseModel):
    try:
        new = await homebases_collection.insert_one(homebase.model_dump())
        created = await homebases_collection.find_one({"_id": new.inserted_id})
        return success_response(homebase_helper(created), msg="Homebases creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el homebase: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_homebases():
    try:
        homebases = [homebase_helper(homebase) async for homebase in homebases_collection.find().sort("homeBaseName", 1)]
        return success_response(homebases, msg="Lista de homebases obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los homebases: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_homebase(id: str):
    homebase = await homebases_collection.find_one({"_id": ObjectId(id)})
    if homebase:
        return success_response(homebase_helper(homebase), msg="HomeBase encontrado")
    return error_response("Homebase no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_homebase(id: str, homebase: HomeBaseModel):
    res = await homebases_collection.update_one({"_id": ObjectId(id)}, {"$set": homebase.model_dump()})
    if res.matched_count == 0:
        return error_response("HomeBase no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await homebases_collection.find_one({"_id": ObjectId(id)})
    return success_response(homebase_helper(updated), msg="Homebase actualizado")

@router.delete("/{id}")
async def delete_homebase(id: str):
    res = await homebases_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="Homebase eliminado")
    return error_response("Homebase no encontrado", status_code=status.HTTP_404_NOT_FOUND)    