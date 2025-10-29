from fastapi import APIRouter, status, Depends
from models.coversheet_model import CoversheetModel
from config.database import coversheets_collection
from schemas.coversheet_scheme import coversheet_helper
from config.dependencies import get_current_user
from utils.response_helper import success_response, error_response
from datetime import datetime, timedelta

from schemas.load_scheme import load_helper
from schemas.downtime_scheme import downtime_helper
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper
from schemas.truck_scheme import truck_helper
from schemas.route_scheme import route_helper
from schemas.homebase_scheme import homebase_helper
from schemas.trailer_scheme import trailer_helper
from schemas.driver_scheme import driver_helper

from config.database import (
    loads_collection,
    downtimes_collection,
    sparetruckinfos_collection,
    trucks_collection,
    homebases_collection,
    trailers_collection,
    drivers_collection
)

from bson import ObjectId

router = APIRouter()

async def expand_related_data(coversheet):
    try:
        loads = [load_helper(await loads_collection.find_one({"_id": ObjectId(load_id)}))
                 for load_id in coversheet.get("load_id", []) if await loads_collection.find_one({"_id": ObjectId(load_id)})]

        downtimes = [downtime_helper(await downtimes_collection.find_one({"_id": ObjectId(dt_id)}))
                     for dt_id in coversheet.get("downtime_id", []) if await downtimes_collection.find_one({"_id": ObjectId(dt_id)})]

        sparetrucks = [sparetruckinfo_helper(await sparetruckinfos_collection.find_one({"_id": ObjectId(sp_id)}))
                       for sp_id in coversheet.get("spareTruckInfo_id", []) if await sparetruckinfos_collection.find_one({"_id": ObjectId(sp_id)})]

        homebase = await homebases_collection.find_one({"_id": ObjectId(coversheet["homebase_id"])})
        truck = await trucks_collection.find_one({"_id": ObjectId(coversheet["truck_id"])})
        trailer = await trailers_collection.find_one({"_id": ObjectId(coversheet["trailer_id"])})
        driver = await drivers_collection.find_one({"_id": ObjectId(coversheet["driver_id"])})

        return {
            **coversheet_helper(coversheet),
            "loads": loads,
            "downtimes": downtimes,
            "spareTruckInfos": sparetrucks,
            "truck": truck_helper(truck) if truck else None,
            "trailer": trailer_helper(trailer) if trailer else None,
            "homebase": homebase_helper(homebase) if homebase else None,
            "driver": driver_helper(driver) if driver else None
        }
    except Exception as e:
        return error_response(f"Error al expandir datos relacionados: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/with-details")
async def get_all_coversheets_with_details():
    try:
        coversheets = [doc async for doc in coversheets_collection.find()]
        result = [await expand_related_data(c) for c in coversheets]
        return success_response(result, msg="Coversheets con detalles obtenidas")
    except Exception as e:
        return error_response(f"Error al obtener coversheets con detalles: {str(e)}")


@router.get("/with-details/{id}")
async def get_coversheet_with_details(id: str):
    try:
        coversheet = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if not coversheet:
            return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)
        return success_response(await expand_related_data(coversheet))
    except Exception as e:
        return error_response(f"Error al obtener coversheet: {str(e)}")


@router.post("/")
async def create_coversheet(coversheet: CoversheetModel):
    try:
        data = coversheet.model_dump()

        # Fetch trailerNumber from trailers_collection
        trailer_id = data.get("trailer_id")
        if trailer_id:
            trailer_doc = await trailers_collection.find_one({"_id": ObjectId(trailer_id)})
            if trailer_doc and trailer_doc.get("trailerNumber"):
                data["trailerNumber"] = trailer_doc["trailerNumber"]
                
        # Fetch truckNumber from trucks_collection
        truck_id = data.get("truck_id")
        if truck_id:
            truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]

        # Fetch homeBaseName from homebase_collection
        homebase_id = data.get("homebase_id")
        if homebase_id:
            homebase_doc = await homebases_collection.find_one({"_id": ObjectId(homebase_id)})
            if homebase_doc and homebase_doc.get("homeBaseName"):
                data["homeBaseName"] = homebase_doc["homeBaseName"]

        # Fetch driverName from drivers_collection
        driver_id = data.get("driver_id")
        if driver_id:
            driver_doc = await drivers_collection.find_one({"_id": ObjectId(driver_id)})
            if driver_doc and driver_doc.get("name"):
                data["driverName"] = driver_doc["name"]

        # Insert the new Coversheet with populated fields
        new = await coversheets_collection.insert_one(data)
        created = await coversheets_collection.find_one({"_id": new.inserted_id})
        return success_response(coversheet_helper(created), msg="Coversheet creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear coversheet: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_coversheets():
    try:
        coversheets = [coversheet_helper(c) async for c in coversheets_collection.find()]
        return success_response(coversheets, msg="Coversheets obtenidas")
    except Exception as e:
        return error_response(f"Error al obtener coversheets: {str(e)}")

from datetime import datetime, timedelta
from fastapi import Query


@router.get("/by-date/{date}")
async def get_coversheets_by_date(date: str):
    try:
        # Convertir string a datetime
        try:
            query_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return error_response("Formato de fecha inválido. Usa YYYY-MM-DD", status_code=status.HTTP_400_BAD_REQUEST)

        # Rango de fecha del día completo
        start = datetime(query_date.year, query_date.month, query_date.day)
        end = start + timedelta(days=1)

        # Buscar coversheets en ese rango
        coversheets = [
            coversheet_helper(c)
            async for c in coversheets_collection.find({
                "date": {"$gte": start, "$lt": end}
            })
        ]

        return success_response(coversheets, msg=f"Coversheets del día {date} obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener coversheets por fecha: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
@router.get("/{id}")
async def get_coversheet(id: str):
    try:
        c = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if c:
            return success_response(coversheet_helper(c))
        return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener coversheet: {str(e)}")


# @router.put("/{id}")
# async def update_coversheet(id: str, coversheet: CoversheetModel):
#     try:
#         data = coversheet.model_dump(exclude_unset=True)

#         # Fetch truckNumber from trucks_collection if truck_id is provided  
#         truck_id = data.get("truck_id")
#         if truck_id:
#             truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
#             if truck_doc and truck_doc.get("truckNumber"):
#                 data["truckNumber"] = truck_doc["truckNumber"]

#         # Fetch routeName from routes_collection if route_id is provided
#         route_id = data.get("route_id")
#         if route_id:
#             route_doc = await routes_collection.find_one({"_id": ObjectId(route_id)})
#             if route_doc and route_doc.get("routeName"):
#                 data["routeName"] = route_doc["routeName"]

#         # Fetch driverName from drivers_collection if driver_id is provided
#         driver_id = data.get("driver_id")
#         if driver_id:
#             driver_doc = await drivers_collection.find_one({"_id": ObjectId(driver_id)})
#             if driver_doc and driver_doc.get("name"):
#                 data["driverName"] = driver_doc["name"]

#         # Update the document with populated fields
#         res = await coversheets_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
#         if res.matched_count == 0:
#             return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)
#         updated = await coversheets_collection.find_one({"_id": ObjectId(id)})
#         return success_response(coversheet_helper(updated), msg="Coversheet actualizada")
#     except Exception as e:
#         return error_response(f"Error al actualizar coversheet: {str(e)}")

@router.put("/{id}")
async def update_coversheet(id: str, coversheet: CoversheetModel):
    try:
        data = coversheet.model_dump(exclude_unset=True)

        # 🔒 Evitar que 'date' sea actualizado
        if "date" in data:
            del data["date"]

        # 🔄 Actualizar la fecha de modificación
        from datetime import datetime, timezone
        data["updatedAt"] = datetime.now(timezone.utc)
        
        # Fetch trailerNumber si se actualizó trailer_id  
        trailer_id = data.get("trailer_id")
        if trailer_id:
            trailer_doc = await trailers_collection.find_one({"_id": ObjectId(trailer_id)})
            if trailer_doc and trailer_doc.get("trailerNumber"):
                data["trailerNumber"] = trailer_doc["trailerNumber"]

        # Fetch truckNumber si se actualizó truck_id  
        truck_id = data.get("truck_id")
        if truck_id:
            truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]

        # Fetch homeBaseName si se actualizó homebase_id
        homebase_id = data.get("homebase_id")
        if homebase_id:
            homebase_doc = await homebases_collection.find_one({"_id": ObjectId(homebase_id)})
            if homebase_doc and homebase_doc.get("homeBaseName"):
                data["homeBaseName"] = homebase_doc["homeBaseName"]

        # Fetch driverName si se actualizó driver_id
        driver_id = data.get("driver_id")
        if driver_id:
            driver_doc = await drivers_collection.find_one({"_id": ObjectId(driver_id)})
            if driver_doc and driver_doc.get("name"):
                data["driverName"] = driver_doc["name"]

        # 💾 Actualizar documento
        res = await coversheets_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        if res.matched_count == 0:
            return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)

        updated = await coversheets_collection.find_one({"_id": ObjectId(id)})
        return success_response(coversheet_helper(updated), msg="Coversheet actualizada exitosamente")
    except Exception as e:
        return error_response(f"Error al actualizar coversheet: {str(e)}")



@router.delete("/{id}")
async def delete_coversheet(id: str):
    try:
        res = await coversheets_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Coversheet eliminada")
        return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar coversheet: {str(e)}")

@router.get("/{id}/sparetruckinfo")
async def get_sparetruckinfo_by_coversheet(id: str):
    from config.database import sparetruckinfos_collection
    from schemas.sparetruckinfo_scheme import sparetruckinfo_helper

    try:
        coversheet = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if not coversheet:
            return error_response("Coversheet no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        spare_ids = coversheet.get("spareTruckInfo_id", [])
        if not spare_ids:
            return success_response([], msg="No hay SpareTruckInfos asociados")

        results = []
        for sp_id in spare_ids:
            doc = await sparetruckinfos_collection.find_one({"_id": ObjectId(sp_id)})
            if doc:
                results.append(sparetruckinfo_helper(doc))

        return success_response(results, msg="SpareTruckInfos obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfos: {str(e)}")

@router.get("/{id}/downtime")
async def get_downtime_by_coversheet(id: str):
    from config.database import downtimes_collection
    from schemas.downtime_scheme import downtime_helper

    try:
        coversheet = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if not coversheet:
            return error_response("Coversheet no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        downtime_ids = coversheet.get("downtime_id", [])
        if not downtime_ids:
            return success_response([], msg="No hay Downtimes asociados")

        results = []
        for do_id in downtime_ids:
            doc = await downtimes_collection.find_one({"_id": ObjectId(do_id)})
            if doc:
                results.append(downtime_helper(doc))

        return success_response(results, msg="Dowmtimes obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener Dowmtimes: {str(e)}")

@router.get("/{id}/load")
async def get_load_by_coversheet(id: str):
    from config.database import loads_collection
    from schemas.load_scheme import load_helper

    try:
        coversheet = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if not coversheet:
            return error_response("Coversheet no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        load_ids = coversheet.get("load_id", [])
        if not load_ids:
            return success_response([], msg="No hay Loads asociados")

        results = []
        for lo_id in load_ids:
            doc = await loads_collection.find_one({"_id": ObjectId(lo_id)})
            if doc:
                results.append(load_helper(doc))

        return success_response(results, msg="Loads obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener Loads: {str(e)}")
