from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from models.downtime_model import DowntimeCreateModel, DowntimeUpdateModel
from config.database import downtimes_collection
from config.database import trucks_collection 
from config.database import trailers_collection
from config.database import typedowntimes_collection
from schemas.downtime_scheme import downtime_helper
from utils.response_helper import success_response, error_response
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_downtime(downtime: DowntimeCreateModel):
    try:
        data = downtime.model_dump()
        coversheet_id = data.pop("coversheet_id")
        
        # Convertir IDs a ObjectId
        for field in ["truck_id", "trailer_id", "typeTruckDownTime_id", "typeTrailerDownTime_id"]:
            if data.get(field):
                data[field] = ObjectId(data[field])
        
        # Campos de auditoría
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        
        # 🔍 Fetch truckNumber from trucks_collection
        truck_id = downtime.truck_id
        if truck_id:
            truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]
                
        # 🔍 Fetch trailerNumber from trailers_collection
        trailer_id = downtime.trailer_id
        if trailer_id:
            trailer_doc = await trailers_collection.find_one({"_id": ObjectId(trailer_id)})
            if trailer_doc and trailer_doc.get("trailerNumber"):
                data["trailerNumber"] = trailer_doc["trailerNumber"] 
                
        # 🔍 Fetch Truck typeDownTimeName from typedowntimes_collection
        typeTruckDownTime_id = downtime.typeTruckDownTime_id
        if typeTruckDownTime_id:
            typeTruckDownTime_doc = await typedowntimes_collection.find_one({"_id": ObjectId(typeTruckDownTime_id)})
            if typeTruckDownTime_doc and typeTruckDownTime_doc.get("typeDownTimeName"):
                data["typeTruckDownTimeName"] = typeTruckDownTime_doc["typeDownTimeName"]       
                
        # 🔍 Fetch Trailer typeDownTimeName from typedowntimes_collection
        typeTrailerDownTime_id = downtime.typeTrailerDownTime_id
        if typeTrailerDownTime_id:
            typeTrailerDownTime_doc = await typedowntimes_collection.find_one({"_id": ObjectId(typeTrailerDownTime_id)})
            if typeTrailerDownTime_doc and typeTrailerDownTime_doc.get("typeDownTimeName"):
                data["typeTrailerDownTimeName"] = typeTrailerDownTime_doc["typeDownTimeName"]   
        
        # Agregar referencia al coversheet
        data["coversheet_ref_id"] = ObjectId(coversheet_id)
        
        # 📦 Insertar el nuevo Downtime 
        new = await downtimes_collection.insert_one(data)
        created = await downtimes_collection.find_one({"_id": new.inserted_id})


        return success_response(downtime_helper(created), msg="Downtime creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear downtime: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_downtimes():
    try:
        downtimes = [downtime_helper(d) async for d in downtimes_collection.find()]
        return success_response(downtimes, msg="Lista de downtimes obtenida")
    except Exception as e:
        return error_response(f"Error al obtener downtimes: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_downtime(id: str):
    try:
        downtime = await downtimes_collection.find_one({"_id": ObjectId(id)})
        if downtime:
            return success_response(downtime_helper(downtime), msg="Downtime encontrada")
        return error_response("Downtime no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener downtime: {str(e)}")
    
@router.put("/{id}")
async def update_downtime(id: str, downtime: DowntimeUpdateModel):
    try:
        # Convertimos el modelo a dict
        data = downtime.model_dump(exclude_unset=True)
        
        # 🔒 Proteger campos que NO deben cambiar
        data.pop("createdAt", None)
        data.pop("updatedAt", None)
        data.pop("coversheet_id", None)
        data.pop("coversheet_ref_id", None)

        # 📄 Actualizar la fecha de modificación
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))
        
        # Convertir IDs a ObjectId
        for field in ["truck_id", "trailer_id", "typeTruckDownTime_id", "typeTrailerDownTime_id"]:
            if data.get(field):
                data[field] = ObjectId(data[field])

        # 🔍 Fetch truckNumber from trucks_collection
        truck_id = downtime.truck_id
        if truck_id:
            truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]
                
        # 🔍 Fetch trailerNumber from trailers_collection
        trailer_id = downtime.trailer_id
        if trailer_id:
            trailer_doc = await trailers_collection.find_one({"_id": ObjectId(trailer_id)})
            if trailer_doc and trailer_doc.get("trailerNumber"):
                data["trailerNumber"] = trailer_doc["trailerNumber"] 
                
        # 🔍 Fetch Truck typeDownTimeName from typedowntimes_collection
        typeTruckDownTime_id = downtime.typeTruckDownTime_id
        if typeTruckDownTime_id:
            typeTruckDownTime_doc = await typedowntimes_collection.find_one({"_id": ObjectId(typeTruckDownTime_id)})
            if typeTruckDownTime_doc and typeTruckDownTime_doc.get("typeDownTimeName"):
                data["typeTruckDownTimeName"] = typeTruckDownTime_doc["typeDownTimeName"]       
                
        # 🔍 Fetch Trailer typeDownTimeName from typedowntimes_collection
        typeTrailerDownTime_id = downtime.typeTrailerDownTime_id
        if typeTrailerDownTime_id:
            typeTrailerDownTime_doc = await typedowntimes_collection.find_one({"_id": ObjectId(typeTrailerDownTime_id)})
            if typeTrailerDownTime_doc and typeTrailerDownTime_doc.get("typeDownTimeName"):
                data["typeTrailerDownTimeName"] = typeTrailerDownTime_doc["typeDownTimeName"]   

        # 🛠️ Actualizar el documento
        res = await downtimes_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response("Downtime no encontrada", status_code=status.HTTP_404_NOT_FOUND)

        updated = await downtimes_collection.find_one({"_id": ObjectId(id)})
        return success_response(downtime_helper(updated), msg="Downtime actualizada")
    
    except Exception as e:
        return error_response(f"Error al actualizar downtime: {str(e)}")


@router.delete("/{id}")
async def delete_downtime(id: str):
    try:
        res = await downtimes_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Downtime eliminada")
        return error_response("Downtime no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar downtime: {str(e)}")