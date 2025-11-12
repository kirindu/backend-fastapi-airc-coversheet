from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.destination_model import DestinationModel
from config.database import destinations_collection
from schemas.destination_scheme import destination_helper
from bson import ObjectId

router = APIRouter()

 
@router.post("/")
async def create_destination(destination: DestinationModel):
    try:
        new = await destinations_collection.insert_one(destination.model_dump())
        created = await destinations_collection.find_one({"_id": new.inserted_id})
        return success_response(destination_helper(created), msg="Destination creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el Destination: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_destinations():
    try:
        destinations = [destination_helper(destination) async for destination in destinations_collection.find().sort("destinationName", 1)]
        return success_response(destinations, msg="Lista de destination obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los destinations: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_destination(id: str):
    destination = await destinations_collection.find_one({"_id": ObjectId(id)})
    if destination:
        return success_response(destination_helper(destination), msg="Destination encontrado")
    return error_response("Destination no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_destination(id: str, destination: DestinationModel):
    res = await destinations_collection.update_one({"_id": ObjectId(id)}, {"$set": destination.model_dump()})
    if res.matched_count == 0:
        return error_response("Destination no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await destinations_collection.find_one({"_id": ObjectId(id)})
    return success_response(destination_helper(updated), msg="Destination actualizado")

@router.delete("/{id}")
async def delete_destination(id: str):
    res = await destinations_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="Destination eliminado")
    return error_response("Destination no encontrado", status_code=status.HTTP_404_NOT_FOUND)    