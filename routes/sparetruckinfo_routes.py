from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from models.sparetruckinfo_model import SpareTruckInfoModel
from config.database import sparetruckinfos_collection
from config.database import trucks_collection
from config.database import trailers_collection
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper
from utils.coversheet_updater import add_entity_to_coversheet
from utils.response_helper import success_response, error_response
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_sparetruckinfo(sparetruckinfo: SpareTruckInfoModel):
    try:
        data = sparetruckinfo.model_dump()
        coversheet_id = data.pop("coversheet_id")

        # Convertir IDs a ObjectId
        for field in ["truck_id", "trailer_id"]:
            if data.get(field):
                data[field] = ObjectId(data[field])
        
        # Campos de auditoría
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        
        # 🔍 Fetch truckNumber from trucks_collection
        truck_id = sparetruckinfo.truck_id
        if truck_id:
            truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]
                
        # 🔍 Fetch trailerNumber from trailers_collection
        trailer_id = sparetruckinfo.trailer_id
        if trailer_id:
            trailer_doc = await trailers_collection.find_one({"_id": ObjectId(trailer_id)})
            if trailer_doc and trailer_doc.get("trailerNumber"):
                data["trailerNumber"] = trailer_doc["trailerNumber"]     
        
        # Agregar referencia al coversheet
        data["coversheet_ref_id"] = ObjectId(coversheet_id)

        # 📦 Insertar el nuevo SpareTruckInfo
        new = await sparetruckinfos_collection.insert_one(data)
        created = await sparetruckinfos_collection.find_one({"_id": new.inserted_id})

        # 🔗 Asociar con coversheet
        await add_entity_to_coversheet(coversheet_id, "spareTruckInfo_id", str(new.inserted_id))

        return success_response(sparetruckinfo_helper(created), msg="SpareTruckInfo creado exitosamente")

    except Exception as e:
        return error_response(f"Error al crear SpareTruckInfo: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_sparetruckinfos():
    try:
        result = [sparetruckinfo_helper(sp) async for sp in sparetruckinfos_collection.find()]
        return success_response(result, msg="Lista de SpareTruckInfos obtenida")
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfos: {str(e)}")

@router.get("/{id}")
async def get_sparetruckinfo(id: str):
    try:
        sparetruckinfo = await sparetruckinfos_collection.find_one({"_id": ObjectId(id)})
        if sparetruckinfo:
            return success_response(sparetruckinfo_helper(sparetruckinfo), msg="SpareTruckInfo encontrado")
        return error_response("SpareTruckInfo no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfo: {str(e)}")
    
@router.put("/{id}")
async def update_sparetruckinfo(id: str, sparetruckinfo: SpareTruckInfoModel):
    try:
        data = sparetruckinfo.model_dump(exclude_unset=True)
        
        # 🔒 Proteger createdAt y coversheet_id: eliminarlos si están presentes
        data.pop("createdAt", None)
        data.pop("coversheet_id", None)  # No permitir cambiar el coversheet

        # 📄 Actualizar la fecha de modificación
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))
        
        # Convertir IDs a ObjectId
        for field in ["truck_id", "trailer_id"]:
            if data.get(field):
                data[field] = ObjectId(data[field])
        
        # 🔍 Fetch truckNumber si se actualizó truck_id  
        truck_id = sparetruckinfo.truck_id
        if truck_id:
            truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]
                
        # 🔍 Fetch trailerNumber si se actualizó trailer_id  
        trailer_id = sparetruckinfo.trailer_id
        if trailer_id:
            trailer_doc = await trailers_collection.find_one({"_id": ObjectId(trailer_id)})
            if trailer_doc and trailer_doc.get("trailerNumber"):
                data["trailerNumber"] = trailer_doc["trailerNumber"]

        # 🛠️ Actualizar el documento
        res = await sparetruckinfos_collection.update_one({"_id": ObjectId(id)}, {"$set": data})

        if res.matched_count == 0:
            return error_response("SpareTruckInfo no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await sparetruckinfos_collection.find_one({"_id": ObjectId(id)})
        return success_response(sparetruckinfo_helper(updated), msg="SpareTruckInfo actualizado")

    except Exception as e:
        return error_response(f"Error al actualizar SpareTruckInfo: {str(e)}")


@router.delete("/{id}")
async def delete_sparetruckinfo(id: str):
    try:
        res = await sparetruckinfos_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="SpareTruckInfo eliminado")
        return error_response("SpareTruckInfo no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar SpareTruckInfo: {str(e)}")