from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.source_model import SourceModel
from config.database import sources_collection
from schemas.source_scheme import source_helper
from bson import ObjectId

router = APIRouter()

 
@router.post("/")
async def create_source(source: SourceModel):
    try:
        new = await sources_collection.insert_one(source.model_dump())
        created = await sources_collection.find_one({"_id": new.inserted_id})
        return success_response(source_helper(created), msg="Source creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el Source: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_sources():
    try:
        sources = [source_helper(source) async for source in sources_collection.find().sort("sourceName", 1)]
        return success_response(sources, msg="Lista de source obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los sources: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_source(id: str):
    source = await sources_collection.find_one({"_id": ObjectId(id)})
    if source:
        return success_response(source_helper(source), msg="Source encontrado")
    return error_response("Source no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_source(id: str, source: SourceModel):
    res = await sources_collection.update_one({"_id": ObjectId(id)}, {"$set": source.model_dump()})
    if res.matched_count == 0:
        return error_response("Source no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await sources_collection.find_one({"_id": ObjectId(id)})
    return success_response(source_helper(updated), msg="Source actualizado")

@router.delete("/{id}")
async def delete_source(id: str):
    res = await sources_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="Source eliminado")
    return error_response("Source no encontrado", status_code=status.HTTP_404_NOT_FOUND)    