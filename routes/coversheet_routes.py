from zoneinfo import ZoneInfo
from fastapi import APIRouter, status, Depends
from models.coversheet_model import CoversheetModel
from config.database import coversheets_collection
from schemas.coversheet_scheme import coversheet_helper
from config.dependencies import get_current_user
from utils.response_helper import success_response, error_response
from datetime import datetime, timedelta
from bson import ObjectId

# Importación de Helpers de otras colecciones
from schemas.load_scheme import load_helper
from schemas.downtime_scheme import downtime_helper
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper

# Importación de Colecciones
from config.database import (
    loads_collection,
    downtimes_collection,
    sparetruckinfos_collection,
    trucks_collection,
    homebases_collection,
    trailers_collection,
    drivers_collection
)

router = APIRouter()

# --- FUNCIONES INTERNAS (HELPERS) ---

async def expand_related_data(coversheet_dict):
    """Agrega la información de loads, downtimes y spares al diccionario de la coversheet."""
    try:
        c_id = ObjectId(coversheet_dict["id"])
        
        # Búsquedas directas por referencia inversa
        loads_cursor = loads_collection.find({"coversheet_ref_id": c_id})
        downtimes_cursor = downtimes_collection.find({"coversheet_ref_id": c_id})
        spares_cursor = sparetruckinfos_collection.find({"coversheet_ref_id": c_id})

        coversheet_dict["loads"] = [load_helper(doc) for doc in await loads_cursor.to_list(length=None)]
        coversheet_dict["downtimes"] = [downtime_helper(doc) for doc in await downtimes_cursor.to_list(length=None)]
        coversheet_dict["spareTruckInfos"] = [sparetruckinfo_helper(doc) for doc in await spares_cursor.to_list(length=None)]
        
        return coversheet_dict
    except Exception as e:
        print(f"Error en expansión de datos: {e}")
        return coversheet_dict
    
async def expand_related_data_from_doc(doc):
    """Expande datos desde el documento de MongoDB original (con ObjectIds)."""
    try:
        c_id = doc["_id"]  # Ya es ObjectId
            
        # Búsquedas directas
        loads_cursor = loads_collection.find({"coversheet_ref_id": c_id})
        downtimes_cursor = downtimes_collection.find({"coversheet_ref_id": c_id})
        spares_cursor = sparetruckinfos_collection.find({"coversheet_ref_id": c_id})

        # Primero convierte el coversheet
        coversheet_dict = coversheet_helper(doc)
            
        # Luego agrega las relaciones
        coversheet_dict["loads"] = [load_helper(d) for d in await loads_cursor.to_list(length=None)]
        coversheet_dict["downtimes"] = [downtime_helper(d) for d in await downtimes_cursor.to_list(length=None)]
        coversheet_dict["spareTruckInfos"] = [sparetruckinfo_helper(d) for d in await spares_cursor.to_list(length=None)]
            
        return coversheet_dict
    except Exception as e:
        print(f"Error en expansión de datos: {e}")
        raise

# --- RUTAS ---

@router.get("/")
async def get_all_coversheets():
    try:
        cursor = coversheets_collection.find().sort("date", -1).limit(50)
        docs = await cursor.to_list(length=50)
        return success_response([coversheet_helper(d) for d in docs])
    except Exception as e:
        return error_response(str(e))

# 1. RUTA DE FECHA (Debe ir antes de {id})
@router.get("/by-date/{date_str}")
async def get_coversheets_by_date(date_str: str):
    """Postman: GET /api/coversheets/by-date/2025-12-24"""
    try:
        try:
            query_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return error_response("Formato inválido. Usa YYYY-MM-DD", status_code=400)

        tz = ZoneInfo("America/Denver")
        start = datetime(query_date.year, query_date.month, query_date.day, tzinfo=tz)
        end = start + timedelta(days=1)

        cursor = coversheets_collection.find({"date": {"$gte": start, "$lt": end}})
        docs = await cursor.to_list(length=None)
        return success_response([coversheet_helper(d) for d in docs])
    except Exception as e:
        return error_response(str(e))

# 2. RUTA DE ID ÚNICO
@router.get("/{id}")
async def get_coversheet_by_id(id: str):
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de Coversheet inválido", status_code=400)
            
        doc = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if not doc:
            return error_response("No encontrada", status_code=404)
        
        # ✅ Expande y retorna directamente (ya está convertido dentro de la función)
        data = await expand_related_data_from_doc(doc)
        return success_response(data)  # ❌ NO llames a coversheet_helper aquí
        
    except Exception as e:
        return error_response(str(e))

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_coversheet(coversheet: CoversheetModel, current_user: str = Depends(get_current_user)):
    try:
        data = coversheet.model_dump()
        
        # Convertir IDs a ObjectId y limpiar obsoletos
        for f in ["truck_id", "trailer_id", "homebase_id", "driver_id"]:
            if data.get(f): data[f] = ObjectId(data[f])
        
        for f in ["load_id", "downtime_id", "spareTruckInfo_id"]:
            data.pop(f, None)

        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["date"] = data["createdAt"].replace(hour=0, minute=0, second=0, microsecond=0)
        data["updatedAt"] = data["createdAt"]

        result = await coversheets_collection.insert_one(data)
        new_doc = await coversheets_collection.find_one({"_id": result.inserted_id})
        return success_response(coversheet_helper(new_doc), msg="Creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear: {str(e)}")

@router.put("/{id}")
async def update_coversheet(id: str, coversheet: CoversheetModel):
    try:
        if not ObjectId.is_valid(id): return error_response("ID inválido", status_code=400)
        
        data = coversheet.model_dump(exclude_unset=True)
        data.pop("date", None) # No permitir cambio de fecha por aquí
        
        # Limpiar y convertir IDs
        for f in ["load_id", "downtime_id", "spareTruckInfo_id"]: data.pop(f, None)
        
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        # Desnormalización de nombres para velocidad
        maps = {
            "truck_id": (trucks_collection, "truckNumber", "truckNumber"),
            "trailer_id": (trailers_collection, "trailerNumber", "trailerNumber"),
            "homebase_id": (homebases_collection, "homeBaseName", "homeBaseName"),
            "driver_id": (drivers_collection, "name", "driverName")
        }

        for field, (col, key, target) in maps.items():
            if field in data:
                data[field] = ObjectId(data[field])
                ref_doc = await col.find_one({"_id": data[field]})
                if ref_doc: data[target] = ref_doc.get(key, "")

        await coversheets_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        updated = await coversheets_collection.find_one({"_id": ObjectId(id)})
        return success_response(coversheet_helper(updated))
    except Exception as e:
        return error_response(str(e))

# 3. RUTAS DE HIJOS (REFERENCIA INVERSA)
@router.get("/{id}/load")
async def get_loads_of_coversheet(id: str):
    if not ObjectId.is_valid(id): return error_response("ID inválido", status_code=400)
    cursor = loads_collection.find({"coversheet_ref_id": ObjectId(id)})
    return success_response([load_helper(d) for d in await cursor.to_list(length=None)])

@router.get("/{id}/downtime")
async def get_downtimes_of_coversheet(id: str):
    if not ObjectId.is_valid(id): return error_response("ID inválido", status_code=400)
    cursor = downtimes_collection.find({"coversheet_ref_id": ObjectId(id)})
    return success_response([downtime_helper(d) for d in await cursor.to_list(length=None)])

@router.get("/{id}/sparetruckinfo")
async def get_spares_of_coversheet(id: str):
    if not ObjectId.is_valid(id): return error_response("ID inválido", status_code=400)
    cursor = sparetruckinfos_collection.find({"coversheet_ref_id": ObjectId(id)})
    return success_response([sparetruckinfo_helper(d) for d in await cursor.to_list(length=None)])

@router.delete("/{id}")
async def delete_coversheet(id: str, current_user: str = Depends(get_current_user)):
    """
    Elimina una coversheet y opcionalmente sus documentos relacionados.
    """
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de Coversheet inválido", status_code=400)
        
        coversheet_id = ObjectId(id)
        
        # Verificar si existe la coversheet
        existing = await coversheets_collection.find_one({"_id": coversheet_id})
        if not existing:
            return error_response("Coversheet no encontrada", status_code=404)
        
        # Eliminar documentos relacionados (loads, downtimes, spareTruckInfos)
        # Si prefieres mantenerlos, comenta estas líneas
        await loads_collection.delete_many({"coversheet_ref_id": coversheet_id})
        await downtimes_collection.delete_many({"coversheet_ref_id": coversheet_id})
        await sparetruckinfos_collection.delete_many({"coversheet_ref_id": coversheet_id})
        
        # Eliminar la coversheet
        result = await coversheets_collection.delete_one({"_id": coversheet_id})
        
        if result.deleted_count == 1:
            return success_response(
                {"id": id}, 
                msg="Coversheet y sus datos relacionados eliminados exitosamente"
            )
        else:
            return error_response("No se pudo eliminar la coversheet", status_code=500)
            
    except Exception as e:
        return error_response(f"Error al eliminar: {str(e)}")