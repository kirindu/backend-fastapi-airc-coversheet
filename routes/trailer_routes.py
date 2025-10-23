from fastapi import APIRouter, status
from models.trailer_model import TrailerModel
from config.database import trailers_collection
from schemas.trailer_scheme import trailer_helper
from utils.response_helper import success_response, error_response
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_trailer(trailer: TrailerModel):
    try:
        new = await trailers_collection.insert_one(trailer.model_dump())
        created = await trailers_collection.find_one({"_id": new.inserted_id})
        return success_response(trailer_helper(created), msg="Trailer creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear Trailer: {str(e)}")

@router.get("/")
async def get_all_trailers():
    try:
        result = [trailer_helper(trailer) async for trailer in trailers_collection.find()]
        return success_response(result, msg="Lista de trailers obtenida")
    except Exception as e:
        return error_response(f"Error al obtener trailers: {str(e)}")

@router.get("/{id}")
async def get_trailer(id: str):
    try:
        trailer = await trailers_collection.find_one({"_id": ObjectId(id)})
        if trailer:
            return success_response(trailer_helper(trailer), msg="Trailer encontrado")
        return error_response("Trailer no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener trailer: {str(e)}")

@router.put("/{id}")
async def update_trailer(id: str, trailer: TrailerModel):
    try:
        res = await trailers_collection.update_one({"_id": ObjectId(id)}, {"$set": trailer.model_dump()})
        if res.matched_count == 0:
            return error_response("Trailer no encontrado", status_code=status.HTTP_404_NOT_FOUND)
        updated = await trailers_collection.find_one({"_id": ObjectId(id)})
        return success_response(trailer_helper(updated), msg="Trailer actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar trailer: {str(e)}")

@router.delete("/{id}")
async def delete_trailer(id: str):
    try:
        res = await trailers_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Trailer eliminado")
        return error_response("Trailer no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar trailer: {str(e)}")
