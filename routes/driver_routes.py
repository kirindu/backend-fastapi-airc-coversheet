from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.driver_model import DriverModel
from config.database import drivers_collection
from schemas.driver_scheme import driver_helper
from config.auth import verify_password, create_access_token, hash_password
from datetime import timedelta
from bson import ObjectId

router = APIRouter()

@router.post("/login")
async def driver_login(driver: DriverModel):
    try:
        db_driver = await drivers_collection.find_one({"username": driver.username})

        if not db_driver or not verify_password(driver.password, db_driver["password"]):
            return error_response("Credenciales inválidas", status_code=status.HTTP_401_UNAUTHORIZED)

        # ✅ Crear token JWT (igual que en user_routes.py)
        access_token = create_access_token(
            data={"sub": db_driver["username"]}, 
            expires_delta=timedelta(minutes=60)
        )

        # ✅ Estructura de respuesta igual a user login
        driver_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(db_driver["_id"]),
                "name": db_driver["name"],
                "username": db_driver["username"],
                "rol": db_driver["rol"]
            }
        }

        return success_response(driver_data, msg="Login exitoso")

    except Exception as e:
        return error_response(f"Error interno al autenticar: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.post("/")
async def create_driver(driver: DriverModel):
    try:
        # ✅ Hash de la contraseña antes de guardar
        driver_dict = driver.model_dump()
        driver_dict["password"] = hash_password(driver_dict["password"])
        
        new = await drivers_collection.insert_one(driver_dict)
        created = await drivers_collection.find_one({"_id": new.inserted_id})
        return success_response(driver_helper(created), msg="Driver creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el driver: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_drivers():
    try:
        drivers = [driver_helper(driver) async for driver in drivers_collection.find().sort("name", 1)]
        return success_response(drivers, msg="Lista de drivers obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los drivers: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_driver(id: str):
    driver = await drivers_collection.find_one({"_id": ObjectId(id)})
    if driver:
        return success_response(driver_helper(driver), msg="Driver encontrado")
    return error_response("Driver no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_driver(id: str, driver: DriverModel):
    try:
        # ✅ Hash de la contraseña si se actualiza
        driver_dict = driver.model_dump()
        driver_dict["password"] = hash_password(driver_dict["password"])
        
        res = await drivers_collection.update_one({"_id": ObjectId(id)}, {"$set": driver_dict})
        if res.matched_count == 0:
            return error_response("Driver no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await drivers_collection.find_one({"_id": ObjectId(id)})
        return success_response(driver_helper(updated), msg="Driver actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar driver: {str(e)}")

@router.delete("/{id}")
async def delete_driver(id: str):
    res = await drivers_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="Driver eliminado")
    return error_response("Driver no encontrado", status_code=status.HTTP_404_NOT_FOUND)