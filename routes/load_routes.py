from fastapi import APIRouter, status, UploadFile, File, Form, HTTPException
from models.load_model import LoadModel
from config.database import loads_collection
from config.database import routes_collection
from config.database import landfills_collection  
from schemas.load_scheme import load_helper
from utils.coversheet_updater import add_entity_to_coversheet
from utils.response_helper import success_response, error_response

from bson import ObjectId
from typing import List, Optional
import os
import uuid

router = APIRouter()

@router.post("/")
async def create_load_with_images(
    firstStopTime: Optional[str] = Form(None),
    route_id: Optional[str] = Form(None),
    lastStopTime: Optional[str] = Form(None),
    landFillTimeIn: Optional[str] = Form(None),
    landFillTimeOut: Optional[str] = Form(None),
    grossWeight: Optional[float] = Form(None),
    tareWeight: Optional[float] = Form(None),
    tons: Optional[float] = Form(None),
    landFill_id: Optional[str] = Form(None),
    ticketNumber: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    coversheet_id: str = Form(...),
    images: List[UploadFile] = File(default=None)  # Cambiar default=[] a default=None para manejar mejor la ausencia de imágenes
):
    try:
        image_paths = []
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        if images:  # Verificar si hay imágenes
            for image in images:
                if not image.content_type.startswith("image/"):
                    return error_response(
                        f"The file '{image.filename}' is not a image.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                contents = await image.read()
                if len(contents) > 5 * 1024 * 1024:
                    return error_response(
                        f"The file '{image.filename}' exceeds the maximum size of 5MB.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                filename = f"{uuid.uuid4()}_{image.filename}"
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(contents)
                image_paths.append(file_path)

        data = {
            "firstStopTime": firstStopTime,
            "route_id": route_id,
            "lastStopTime": lastStopTime,
            "landFillTimeIn": landFillTimeIn,
            "landFillTimeOut": landFillTimeOut,
            "grossWeight": grossWeight,
            "tareWeight": tareWeight,
            "tons": tons,
            "landFill_id": landFill_id,
            "ticketNumber": ticketNumber,
            "note": note,
            "images": image_paths if image_paths else []  # Asegurar que 'images' siempre sea una lista
        }
        
# 🔍 Obtener routeName si hay route_id
        if route_id:
            try:
                route_doc = await routes_collection.find_one({"_id": ObjectId(route_id)})
                if route_doc and route_doc.get("routeName"):
                    data["routeName"] = route_doc["routeName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar route Name: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)
            
            
# 🔍 Obtener landfillName si hay landfill_id
        if landFill_id:
            try:
                landfill_doc = await landfills_collection.find_one({"_id": ObjectId(landFill_id)})
                if landfill_doc and landfill_doc.get("landfillName"):
                    data["landfillName"] = landfill_doc["landfillName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar landfillName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)


        new = await loads_collection.insert_one(data)
        created = await loads_collection.find_one({"_id": new.inserted_id})
        await add_entity_to_coversheet(coversheet_id, "load_id", str(new.inserted_id))

        return success_response(load_helper(created), msg="Load created successfully")
    except Exception as e:
        return error_response(f"Error creating load: {str(e)}")

@router.put("/{id}")
async def update_load_with_form(
    id: str,
    firstStopTime: Optional[str] = Form(None),
    route_id: Optional[str] = Form(None),
    lastStopTime: Optional[str] = Form(None),
    landFillTimeIn: Optional[str] = Form(None),
    landFillTimeOut: Optional[str] = Form(None),
    grossWeight: Optional[float] = Form(None),
    tareWeight: Optional[float] = Form(None),
    tons: Optional[float] = Form(None),
    landFill_id: Optional[str] = Form(None),
    ticketNumber: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=None)
):
    try:
        existing = await loads_collection.find_one({"_id": ObjectId(id)})
        if not existing:
            return error_response("Load not found", status_code=status.HTTP_404_NOT_FOUND)

        image_paths = existing.get("images", [])
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        if images:  # Verificar si hay nuevas imágenes
            for image in images:
                if not image.content_type.startswith("image/"):
                    return error_response(
                        f"El archivo '{image.filename}' no es una imagen válida.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                contents = await image.read()
                if len(contents) > 5 * 1024 * 1024:
                    return error_response(
                        f"The image '{image.filename}' exceeds the maximum allowed size of 5MB.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                filename = f"{uuid.uuid4()}_{image.filename}"
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(contents)
                image_paths.append(file_path)

        data = {
            "firstStopTime": firstStopTime,
            "route_id": route_id,
            "lastStopTime": lastStopTime,
            "landFillTimeIn": landFillTimeIn,
            "landFillTimeOut": landFillTimeOut,
            "grossWeight": grossWeight,
            "tareWeight": tareWeight,
            "tons": tons,
            "landFill_id": landFill_id,
            "ticketNumber": ticketNumber,
            "note": note,
            "images": image_paths
        }
        
        # 🔍 Obtener routeName si hay route_id
        if route_id:
            try:
                route_doc = await routes_collection.find_one({"_id": ObjectId(route_id)})
                if route_doc and route_doc.get("routeName"):
                    data["routeName"] = route_doc["routeName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar routeName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)

        
# 🔍 Obtener landfillName si hay landfill_id
        if landFill_id:
            try:
                landfill_doc = await landfills_collection.find_one({"_id": ObjectId(landFill_id)})
                if landfill_doc and landfill_doc.get("landfillName"):
                    data["landfillName"] = landfill_doc["landfillName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar landfillName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)
            
            # 🔍 Obtener landfillName si hay landfill_id
        if landFill_id:
            try:
                landfill_doc = await landfills_collection.find_one({"_id": ObjectId(landFill_id)})
                if landfill_doc and landfill_doc.get("landfillName"):
                    data["landfillName"] = landfill_doc["landfillName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar landfillName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)


        res = await loads_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        updated = await loads_collection.find_one({"_id": ObjectId(id)})
        return success_response(load_helper(updated), msg="Load actualizada")
    except Exception as e:
        return error_response(f"Error updating load: {str(e)}")

@router.get("/")
async def get_all_loads():
    try:
        loads = [load_helper(load) async for load in loads_collection.find()]
        return success_response(loads, msg="Lista de loads obtenida")
    except Exception as e:
        return error_response(f"Error al obtener loads: {str(e)}")


@router.get("/{id}")
async def get_load(id: str):
    try:
        load = await loads_collection.find_one({"_id": ObjectId(id)})
        if load:
            return success_response(load_helper(load), msg="Load encontrada")
        return error_response("Load no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener load: {str(e)}")


@router.delete("/{id}")
async def delete_load(id: str):
    try:
        res = await loads_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Load eliminada")
        return error_response("Load no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar load: {str(e)}")
