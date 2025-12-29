from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from models.sparetruckinfo_model import SpareTruckInfoCreateModel, SpareTruckInfoUpdateModel
from config.database import sparetruckinfos_collection
from config.database import trucks_collection
from config.database import trailers_collection
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper
from utils.response_helper import success_response, error_response
from datetime import datetime
from bson import ObjectId

router = APIRouter()


async def fetch_and_embed_related_data(data: dict, sparetruckinfo_input) -> dict:
    """Helper function para traer y embeber datos relacionados"""
    
    # 🚛 Fetch truckNumber from trucks_collection
    truck_id = sparetruckinfo_input.truck_id if hasattr(sparetruckinfo_input, 'truck_id') else None
    if truck_id:
        truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
        if truck_doc and truck_doc.get("truckNumber"):
            data["truckNumber"] = truck_doc["truckNumber"]
    
    # 🚚 Fetch trailerNumber from trailers_collection
    trailer_id = sparetruckinfo_input.trailer_id if hasattr(sparetruckinfo_input, 'trailer_id') else None
    if trailer_id:
        trailer_doc = await trailers_collection.find_one({"_id": ObjectId(trailer_id)})
        if trailer_doc and trailer_doc.get("trailerNumber"):
            data["trailerNumber"] = trailer_doc["trailerNumber"]
    
    return data


@router.post("/")
async def create_sparetruckinfo(sparetruckinfo: SpareTruckInfoCreateModel):
    """Crear un nuevo sparetruckinfo - requiere coversheet_id"""
    try:
        data = sparetruckinfo.model_dump()
        coversheet_id = data.pop("coversheet_id")

        # Remover campos de auditoría si vienen en el request
        data.pop("createdAt", None)
        data.pop("updatedAt", None)

        # Convertir IDs a ObjectId
        for field in ["truck_id", "trailer_id"]:
            if data.get(field):
                data[field] = ObjectId(data[field])
        
        # Campos de auditoría
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        
        # Fetch y embeber datos relacionados
        data = await fetch_and_embed_related_data(data, sparetruckinfo)
        
        # Agregar referencia al coversheet
        data["coversheet_ref_id"] = ObjectId(coversheet_id)

        # 📦 Insertar el nuevo SpareTruckInfo
        new = await sparetruckinfos_collection.insert_one(data)
        created = await sparetruckinfos_collection.find_one({"_id": new.inserted_id})

        return success_response(
            sparetruckinfo_helper(created), 
            msg="SpareTruckInfo creado exitosamente"
        )

    except Exception as e:
        return error_response(
            f"Error al crear SpareTruckInfo: {str(e)}", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_sparetruckinfos():
    """Obtener todos los sparetruckinfos"""
    try:
        result = [sparetruckinfo_helper(sp) async for sp in sparetruckinfos_collection.find()]
        return success_response(result, msg="Lista de SpareTruckInfos obtenida")
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfos: {str(e)}")


@router.get("/{id}")
async def get_sparetruckinfo(id: str):
    """Obtener un sparetruckinfo por ID"""
    try:
        sparetruckinfo = await sparetruckinfos_collection.find_one({"_id": ObjectId(id)})
        if sparetruckinfo:
            return success_response(
                sparetruckinfo_helper(sparetruckinfo), 
                msg="SpareTruckInfo encontrado"
            )
        return error_response(
            "SpareTruckInfo no encontrado", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfo: {str(e)}")

    
@router.put("/{id}")
async def update_sparetruckinfo(id: str, sparetruckinfo: SpareTruckInfoUpdateModel):
    """Actualizar un sparetruckinfo existente - NO requiere coversheet_id"""
    try:
        # Convertimos el modelo a dict (solo campos enviados)
        data = sparetruckinfo.model_dump(exclude_unset=True)
        
        # 🔒 Proteger campos que NO deben cambiar
        data.pop("createdAt", None)
        data.pop("coversheet_id", None)
        data.pop("coversheet_ref_id", None)

        # Si no hay datos para actualizar, retornar error
        if not data:
            return error_response(
                "No se proporcionaron campos para actualizar",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # 🔄 Actualizar la fecha de modificación
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))
        
        # Convertir IDs a ObjectId solo si están presentes
        for field in ["truck_id", "trailer_id"]:
            if field in data and data[field]:
                data[field] = ObjectId(data[field])
        
        # Fetch y embeber datos relacionados solo si los IDs cambiaron
        data = await fetch_and_embed_related_data(data, sparetruckinfo)

        # 🛠️ Actualizar el documento
        res = await sparetruckinfos_collection.update_one(
            {"_id": ObjectId(id)}, 
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "SpareTruckInfo no encontrado", 
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await sparetruckinfos_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            sparetruckinfo_helper(updated), 
            msg="SpareTruckInfo actualizado"
        )

    except Exception as e:
        return error_response(f"Error al actualizar SpareTruckInfo: {str(e)}")


@router.delete("/{id}")
async def delete_sparetruckinfo(id: str):
    """Eliminar un sparetruckinfo"""
    try:
        res = await sparetruckinfos_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="SpareTruckInfo eliminado")
        return error_response(
            "SpareTruckInfo no encontrado", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al eliminar SpareTruckInfo: {str(e)}")