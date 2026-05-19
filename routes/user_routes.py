from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from config.auth import verify_password, create_access_token, hash_password
from datetime import timedelta
from models.user_model import UserModel
from config.database import users_collection
from schemas.user_scheme import user_helper
from bson import ObjectId
from config.dependencies import get_current_user
from utils.response_helper import success_response, error_response

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await users_collection.find_one({"email": form_data.username})
        if not user or not verify_password(form_data.password, user["password"]):
            return error_response("Credenciales inválidas", status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token(
            data={"sub": user["email"]}
            #expires_delta=timedelta(minutes=60)
        )

        return success_response({
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "rol": user["rol"]
            }
        }, msg="Login exitoso")
    except Exception as e:
        return error_response(f"Error al iniciar sesión: {str(e)}")


@router.post("/")
async def create_user(user: UserModel):
    try:
        user_dict = user.model_dump()
        user_dict["password"] = hash_password(user_dict["password"])
        new = await users_collection.insert_one(user_dict)
        created = await users_collection.find_one({"_id": new.inserted_id})
        return success_response(user_helper(created), msg="Usuario creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear usuario: {str(e)}")

@router.get("/")
async def get_all_users():
    try:
        users = [user_helper(user) async for user in users_collection.find()]
        return success_response(users, msg="Lista de usuarios obtenida")
    except Exception as e:
        return error_response(f"Error al obtener usuarios: {str(e)}")

@router.get("/{id}")
async def get_user(id: str):
    try:
        user = await users_collection.find_one({"_id": ObjectId(id)})
        if user:
            return success_response(user_helper(user), msg="Usuario encontrado")
        return error_response("Usuario no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener usuario: {str(e)}")

@router.put("/{id}")
async def update_user(id: str, user: UserModel):
    try:
        user_dict = user.model_dump()
        user_dict["password"] = hash_password(user_dict["password"])  # 👈 importante

        res = await users_collection.update_one({"_id": ObjectId(id)}, {"$set": user_dict})
        if res.matched_count == 0:
            return error_response("Usuario no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await users_collection.find_one({"_id": ObjectId(id)})
        return success_response(user_helper(updated), msg="Usuario actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar usuario: {str(e)}")

@router.delete("/{id}")
async def delete_user(id: str, current_user: dict = Depends(get_current_user)):
    try:
        if current_user.get("rol") != "Admin":
            return error_response("No tienes permiso para eliminar usuarios", status_code=status.HTTP_403_FORBIDDEN)

        res = await users_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Usuario eliminado")
        return error_response("Usuario no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar usuario: {str(e)}")
