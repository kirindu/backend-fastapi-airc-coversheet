from fastapi import APIRouter, status, UploadFile, File, Form, HTTPException
from models.load_model import LoadModel
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from config.database import loads_collection
from config.database import routes_collection
from config.database import landfills_collection  
from config.database import sources_collection
from config.database import destinations_collection
from config.database import materials_collection
from config.database import operators_collection

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
    
    tunnelTimeInLoad: Optional[str] = Form(None),
    tunnelTimeOutLoad: Optional[str] = Form(None),
    leaveYardLoad: Optional[str] = Form(None),
    timeInLoad: Optional[str] = Form(None),
    timeOutLoad: Optional[str] = Form(None),
    ticketNumberLoad: Optional[str] = Form(None),
    grossWeightLoad: Optional[str] = Form(None),
    tareWeightLoad: Optional[str] = Form(None),
    tonsLoad: Optional[str] = Form(None),
    backYardLoad: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=None),
    image_path: Optional[str] = Form(None),
    noteLoad: Optional[str] = Form(None),
    preloadedLoad: Optional[bool] = Form(False),
    preloadedNextDayLoad: Optional[bool] = Form(False),
    
    operator_id: Optional[str] = Form(None),
    source_id: Optional[str] = Form(None),
    destination_id: Optional[str] = Form(None),
    material_id: Optional[str] = Form(None),
    coversheet_id: str = Form(...),
):
    try:
        image_paths = []
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        if images:
            for image in images:
                if not image or not image.filename:
                    continue
                
                if not image.content_type or not image.content_type.startswith("image/"):
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
            "tunnelTimeInLoad": tunnelTimeInLoad,
            "tunnelTimeOutLoad": tunnelTimeOutLoad,
            "leaveYardLoad": leaveYardLoad,
            "timeInLoad": timeInLoad,
            "timeOutLoad": timeOutLoad,
            "ticketNumberLoad": ticketNumberLoad,
            "grossWeightLoad": grossWeightLoad,
            "tareWeightLoad": tareWeightLoad,
            "tonsLoad": tonsLoad,
            "backYardLoad": backYardLoad,
            "preloadedLoad": preloadedLoad,
            "preloadedNextDayLoad": preloadedNextDayLoad,
            "noteLoad": noteLoad,
            "images": image_paths if image_paths else [],
            "image_path": image_path,
            "operator_id": operator_id,
            "source_id": source_id,
            "destination_id": destination_id,
            "material_id": material_id,
        }
        
        # Convertir IDs a ObjectId
        for field in ["operator_id", "source_id", "destination_id", "material_id"]:
            if data.get(field):
                data[field] = ObjectId(data[field])
        
        # ✅ Guardar coversheet_ref_id (NO coversheet_id)
        data["coversheet_ref_id"] = ObjectId(coversheet_id)
        
        # Campos de auditoría
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        
        # 🔍 Obtener Operador
        if operator_id:
            try:
                operator_doc = await operators_collection.find_one({"_id": ObjectId(operator_id)})
                if operator_doc and operator_doc.get("operatorName"):
                    data["operatorName"] = operator_doc["operatorName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar operatorName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)

        # 🔍 Obtener Source
        if source_id:
            try:
                source_doc = await sources_collection.find_one({"_id": ObjectId(source_id)})
                if source_doc and source_doc.get("sourceName"):
                    data["sourceName"] = source_doc["sourceName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar sourceName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)

        # 🔍 Obtener Destination
        if destination_id:
            try:
                destination_doc = await destinations_collection.find_one({"_id": ObjectId(destination_id)})
                if destination_doc and destination_doc.get("destinationName"):
                    data["destinationName"] = destination_doc["destinationName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar destinationName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)
            
        # 🔍 Obtener Material
        if material_id:
            try:
                material_doc = await materials_collection.find_one({"_id": ObjectId(material_id)})
                if material_doc and material_doc.get("materialName"):
                    data["materialName"] = material_doc["materialName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar materialName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)

        new = await loads_collection.insert_one(data)
        created = await loads_collection.find_one({"_id": new.inserted_id})
        await add_entity_to_coversheet(coversheet_id, "load_id", str(new.inserted_id))

        return success_response(load_helper(created), msg="Load created successfully")
    except Exception as e:
        return error_response(f"Error creating load: {str(e)}")

@router.put("/{id}")
async def update_load_with_form(
    id: str,
    tunnelTimeInLoad: Optional[str] = Form(None),
    tunnelTimeOutLoad: Optional[str] = Form(None),
    leaveYardLoad: Optional[str] = Form(None),
    timeInLoad: Optional[str] = Form(None),
    timeOutLoad: Optional[str] = Form(None),
    ticketNumberLoad: Optional[str] = Form(None),
    grossWeightLoad: Optional[str] = Form(None),
    tareWeightLoad: Optional[str] = Form(None),
    tonsLoad: Optional[str] = Form(None),
    backYardLoad: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=None),
    image_path: Optional[str] = Form(None),
    noteLoad: Optional[str] = Form(None),
    preloadedLoad: Optional[bool] = Form(False),
    preloadedNextDayLoad: Optional[bool] = Form(False),
    
    operator_id: Optional[str] = Form(None),
    source_id: Optional[str] = Form(None),
    destination_id: Optional[str] = Form(None),
    material_id: Optional[str] = Form(None),
):
    try:
        existing = await loads_collection.find_one({"_id": ObjectId(id)})
        if not existing:
            return error_response("Load not found", status_code=status.HTTP_404_NOT_FOUND)

        image_paths = existing.get("images", [])
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        if images:
            for image in images:
                if not image or not image.filename:
                    continue
                
                if not image.content_type or not image.content_type.startswith("image/"):
                    return error_response(
                        f"The file '{image.filename}' is not a image.",
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
            "tunnelTimeInLoad": tunnelTimeInLoad,
            "tunnelTimeOutLoad": tunnelTimeOutLoad,
            "leaveYardLoad": leaveYardLoad,
            "timeInLoad": timeInLoad,
            "timeOutLoad": timeOutLoad,
            "ticketNumberLoad": ticketNumberLoad,
            "grossWeightLoad": grossWeightLoad,
            "tareWeightLoad": tareWeightLoad,
            "tonsLoad": tonsLoad,
            "backYardLoad": backYardLoad,
            "preloadedLoad": preloadedLoad,
            "preloadedNextDayLoad": preloadedNextDayLoad,
            "noteLoad": noteLoad,
            "operator_id": operator_id,
            "source_id": source_id,
            "destination_id": destination_id,
            "material_id": material_id,
            "images": image_paths,
            "image_path": image_path
        }
        
        # Convertir IDs a ObjectId
        for field in ["operator_id", "source_id", "destination_id", "material_id"]:
            if data.get(field):
                data[field] = ObjectId(data[field])
        
        # Campos de auditoría
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))
        
        # 🔍 Obtener Operador
        if operator_id:
            try:
                operator_doc = await operators_collection.find_one({"_id": ObjectId(operator_id)})
                if operator_doc and operator_doc.get("operatorName"):
                    data["operatorName"] = operator_doc["operatorName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar operatorName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)

        # 🔍 Obtener Source
        if source_id:
            try:
                source_doc = await sources_collection.find_one({"_id": ObjectId(source_id)})
                if source_doc and source_doc.get("sourceName"):
                    data["sourceName"] = source_doc["sourceName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar sourceName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)

        # 🔍 Obtener Destination
        if destination_id:
            try:
                destination_doc = await destinations_collection.find_one({"_id": ObjectId(destination_id)})
                if destination_doc and destination_doc.get("destinationName"):
                    data["destinationName"] = destination_doc["destinationName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar destinationName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)
            
        # 🔍 Obtener Material
        if material_id:
            try:
                material_doc = await materials_collection.find_one({"_id": ObjectId(material_id)})
                if material_doc and material_doc.get("materialName"):
                    data["materialName"] = material_doc["materialName"]
            except Exception as lookup_error:
                return error_response(f"Error al buscar materialName: {str(lookup_error)}", status_code=status.HTTP_400_BAD_REQUEST)

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