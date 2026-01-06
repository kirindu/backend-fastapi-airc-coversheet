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
async def get_all_coversheets(
    page: int = 1,
    limit: int = 50,
    start_date: str = None,
    end_date: str = None,
    truck_id: str = None,
    trailer_id: str = None,
    driver_id: str = None,
    homebase_id: str = None,
    sort_by: str = "date",
    sort_order: int = -1
):
    """
    Obtiene coversheets con paginación y filtros.
    
    Ejemplos:
    - GET /api/coversheets/ → Primera página (50 registros)
    - GET /api/coversheets/?page=2&limit=100 → Segunda página (100 registros)
    - GET /api/coversheets/?start_date=2025-01-01&end_date=2025-12-31
    - GET /api/coversheets/?driver_id=ABC123&truck_id=XYZ789
    """
    try:
        # Validar parámetros
        if page < 1:
            return error_response("El parámetro 'page' debe ser >= 1", status_code=400)
        if limit < 1 or limit > 500:
            return error_response("El parámetro 'limit' debe estar entre 1 y 500", status_code=400)
        
        # ✅ Construir query de filtros - SOLO coversheets activos
        query = {"active": True}
        tz = ZoneInfo("America/Denver")
        
        # Filtro de fechas
        if start_date or end_date:
            date_filter = {}
            if start_date:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    start = start.replace(tzinfo=tz)
                    date_filter["$gte"] = start
                except ValueError:
                    return error_response("Formato de start_date inválido. Usa YYYY-MM-DD", status_code=400)
            
            if end_date:
                try:
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    end = end.replace(tzinfo=tz) + timedelta(days=1)
                    date_filter["$lt"] = end
                except ValueError:
                    return error_response("Formato de end_date inválido. Usa YYYY-MM-DD", status_code=400)
            
            if date_filter:
                query["date"] = date_filter
        
        # Filtros por IDs (convertir strings a ObjectId)
        if truck_id:
            if ObjectId.is_valid(truck_id):
                query["truck_id"] = ObjectId(truck_id)
            else:
                return error_response("truck_id inválido", status_code=400)
                
        if trailer_id:
            if ObjectId.is_valid(trailer_id):
                query["trailer_id"] = ObjectId(trailer_id)
            else:
                return error_response("trailer_id inválido", status_code=400)
                
        if driver_id:
            if ObjectId.is_valid(driver_id):
                query["driver_id"] = ObjectId(driver_id)
            else:
                return error_response("driver_id inválido", status_code=400)
                
        if homebase_id:
            if ObjectId.is_valid(homebase_id):
                query["homebase_id"] = ObjectId(homebase_id)
            else:
                return error_response("homebase_id inválido", status_code=400)
        
        # Calcular skip para paginación
        skip = (page - 1) * limit
        
        # Contar total de documentos que coinciden con los filtros
        total_count = await coversheets_collection.count_documents(query)
        
        # Obtener documentos con paginación
        cursor = coversheets_collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        # Procesar documentos
        coversheets = [coversheet_helper(d) for d in docs]
        
        # Calcular metadata de paginación
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return success_response({
            "data": coversheets,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "truck_id": truck_id,
                "trailer_id": trailer_id,
                "driver_id": driver_id,
                "homebase_id": homebase_id,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        })
    except Exception as e:
        return error_response(f"Error al obtener coversheets: {str(e)}")

@router.get("/{id}")
async def get_coversheet_with_details(id: str):
    """Obtiene un coversheet específico con todos sus datos relacionados."""
    try:
        if not ObjectId.is_valid(id): 
            return error_response("ID inválido", status_code=400)
        
        # ✅ Buscar coversheet activo
        doc = await coversheets_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        
        if not doc:
            return error_response("Coversheet no encontrada o está inactiva", status_code=404)
        
        # Expandir con loads, downtimes y spares
        result = await expand_related_data_from_doc(doc)
        return success_response(result)
        
    except Exception as e:
        return error_response(str(e))

@router.post("/")
async def create_coversheet(coversheet: CoversheetModel):
    try:
        # ✅ PASO 1: Usar exclude_unset para obtener solo los campos enviados
        data = coversheet.model_dump(exclude_unset=True)
        
        # ✅ PASO 2: Limpiar campos obsoletos
        for f in ["load_id", "downtime_id", "spareTruckInfo_id"]: 
            data.pop(f, None)
        
        # ✅ PASO 3: Establecer timestamps
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        
        # ✅ NUEVA LÓGICA: Solo establecer date si no fue enviado por el usuario
        if "date" not in data:
            data["date"] = data["createdAt"].replace(hour=0, minute=0, second=0, microsecond=0)
        
        data["updatedAt"] = data["createdAt"]
        data["active"] = True

        # ✅ PASO 4: Desnormalización de nombres para velocidad
        maps = {
            "truck_id": (trucks_collection, "truckNumber", "truckNumber"),
            "trailer_id": (trailers_collection, "trailerNumber", "trailerNumber"),
            "homebase_id": (homebases_collection, "homeBaseName", "homeBaseName"),
            "driver_id": (drivers_collection, "name", "driverName")
        }

        for field, (col, key, target) in maps.items():
            if field in data:
                # Convertir string ID a ObjectId
                data[field] = ObjectId(data[field])
                
                # Buscar el documento relacionado
                ref_doc = await col.find_one({"_id": data[field]})
                
                # Guardar el nombre en el campo desnormalizado
                if ref_doc: 
                    data[target] = ref_doc.get(key, "")

        # ✅ PASO 5: Insertar en la base de datos
        result = await coversheets_collection.insert_one(data)
        
        # ✅ PASO 6: Recuperar el documento insertado y devolverlo
        new_doc = await coversheets_collection.find_one({"_id": result.inserted_id})
        return success_response(coversheet_helper(new_doc), msg="Creada exitosamente")
        
    except Exception as e:
        return error_response(f"Error al crear: {str(e)}")

@router.put("/{id}")
async def update_coversheet(id: str, coversheet: CoversheetModel):
    try:
        if not ObjectId.is_valid(id): 
            return error_response("ID inválido", status_code=400)
        
        # ✅ PASO 1: Usar exclude_unset para obtener solo los campos enviados
        data = coversheet.model_dump(exclude_unset=True)
        
        # ✅ PASO 2: Limpiar campos obsoletos
        for f in ["load_id", "downtime_id", "spareTruckInfo_id"]: 
            data.pop(f, None)
        
        # ✅ PASO 3: Actualizar updatedAt
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))
        
        # ✅ NUEVA LÓGICA: Permitir actualización de date solo si fue enviado
        # (si no fue enviado, exclude_unset ya se encargó de no incluirlo en data)

        # ✅ PASO 4: Desnormalización de nombres para velocidad
        maps = {
            "truck_id": (trucks_collection, "truckNumber", "truckNumber"),
            "trailer_id": (trailers_collection, "trailerNumber", "trailerNumber"),
            "homebase_id": (homebases_collection, "homeBaseName", "homeBaseName"),
            "driver_id": (drivers_collection, "name", "driverName")
        }

        for field, (col, key, target) in maps.items():
            if field in data:
                # Convertir string ID a ObjectId
                data[field] = ObjectId(data[field])
                
                # Buscar el documento relacionado
                ref_doc = await col.find_one({"_id": data[field]})
                
                # Guardar el nombre en el campo desnormalizado
                if ref_doc: 
                    data[target] = ref_doc.get(key, "")

        # ✅ PASO 5: Actualizar en la base de datos (solo si está activo)
        result = await coversheets_collection.update_one(
            {"_id": ObjectId(id), "active": True}, 
            {"$set": data}
        )
        
        if result.matched_count == 0:
            return error_response("Coversheet no encontrada o está inactiva", status_code=404)
        
        # ✅ PASO 6: Recuperar el documento actualizado y devolverlo
        updated = await coversheets_collection.find_one({"_id": ObjectId(id)})
        return success_response(coversheet_helper(updated))
        
    except Exception as e:
        return error_response(str(e))

# 3. RUTAS DE HIJOS (REFERENCIA INVERSA)
@router.get("/{id}/load")
async def get_loads_of_coversheet(id: str):
    if not ObjectId.is_valid(id): 
        return error_response("ID inválido", status_code=400)
    
    # ✅ Verificar que el coversheet existe y está activo
    coversheet = await coversheets_collection.find_one({
        "_id": ObjectId(id),
        "active": True
    })
    if not coversheet:
        return error_response("Coversheet no encontrada o está inactiva", status_code=404)
    
    cursor = loads_collection.find({"coversheet_ref_id": ObjectId(id)})
    return success_response([load_helper(d) for d in await cursor.to_list(length=None)])

@router.get("/{id}/downtime")
async def get_downtimes_of_coversheet(id: str):
    if not ObjectId.is_valid(id): 
        return error_response("ID inválido", status_code=400)
    
    # ✅ Verificar que el coversheet existe y está activo
    coversheet = await coversheets_collection.find_one({
        "_id": ObjectId(id),
        "active": True
    })
    if not coversheet:
        return error_response("Coversheet no encontrada o está inactiva", status_code=404)
    
    cursor = downtimes_collection.find({"coversheet_ref_id": ObjectId(id)})
    return success_response([downtime_helper(d) for d in await cursor.to_list(length=None)])

@router.get("/{id}/sparetruckinfo")
async def get_spares_of_coversheet(id: str):
    if not ObjectId.is_valid(id): 
        return error_response("ID inválido", status_code=400)
    
    # ✅ Verificar que el coversheet existe y está activo
    coversheet = await coversheets_collection.find_one({
        "_id": ObjectId(id),
        "active": True
    })
    if not coversheet:
        return error_response("Coversheet no encontrada o está inactiva", status_code=404)
    
    cursor = sparetruckinfos_collection.find({"coversheet_ref_id": ObjectId(id)})
    return success_response([sparetruckinfo_helper(d) for d in await cursor.to_list(length=None)])

# ✅ BORRADO LÓGICO - Cambia active de true a false
@router.delete("/{id}")
async def delete_coversheet(id: str, current_user: str = Depends(get_current_user)):
    """
    Realiza un borrado lógico de una coversheet cambiando active de true a false.
    Los documentos relacionados (loads, downtimes, spareTruckInfos) no se eliminan.
    """
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de Coversheet inválido", status_code=400)
        
        coversheet_id = ObjectId(id)
        
        # Verificar si existe la coversheet y está activa
        existing = await coversheets_collection.find_one({
            "_id": coversheet_id,
            "active": True
        })
        if not existing:
            return error_response("Coversheet no encontrada o ya está inactiva", status_code=404)
        
        # ✅ Borrado lógico: cambiar active a false
        result = await coversheets_collection.update_one(
            {"_id": coversheet_id},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        if result.modified_count == 1:
            return success_response(
                {"id": id, "active": False}, 
                msg="Coversheet desactivada exitosamente (borrado lógico)"
            )
        else:
            return error_response("No se pudo desactivar la coversheet", status_code=500)
            
    except Exception as e:
        return error_response(f"Error al desactivar: {str(e)}")

# ✅ BORRADO FÍSICO (OPCIONAL) - Elimina permanentemente
@router.delete("/{id}/hard-delete")
async def hard_delete_coversheet(id: str, current_user: str = Depends(get_current_user)):
    """
    Elimina PERMANENTEMENTE una coversheet y sus documentos relacionados.
    ⚠️ ADVERTENCIA: Esta acción NO se puede deshacer.
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
        await loads_collection.delete_many({"coversheet_ref_id": coversheet_id})
        await downtimes_collection.delete_many({"coversheet_ref_id": coversheet_id})
        await sparetruckinfos_collection.delete_many({"coversheet_ref_id": coversheet_id})
        
        # Eliminar la coversheet permanentemente
        result = await coversheets_collection.delete_one({"_id": coversheet_id})
        
        if result.deleted_count == 1:
            return success_response(
                {"id": id}, 
                msg="Coversheet y sus datos relacionados eliminados PERMANENTEMENTE"
            )
        else:
            return error_response("No se pudo eliminar la coversheet", status_code=500)
            
    except Exception as e:
        return error_response(f"Error al eliminar permanentemente: {str(e)}")