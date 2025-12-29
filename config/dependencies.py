from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.auth import decode_token
from config.database import users_collection, drivers_collection
from bson import ObjectId

# Cambiar de OAuth2PasswordBearer a HTTPBearer para soportar Authorization: Bearer
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency para obtener el usuario actual desde el token JWT.
    Busca tanto en users (admins) como en drivers.
    """
    token = credentials.credentials
    
    try:
        # Decodificar el token
        payload = decode_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
        
        # El 'sub' puede ser email (users) o username (drivers)
        identifier = payload.get("sub")
        
        if not identifier:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # ✅ Intentar buscar primero en users (por email)
        user = await users_collection.find_one({"email": identifier})
        
        if user:
            return {
                "id": str(user["_id"]),
                "name": user.get("name"),
                "email": user.get("email"),
                "rol": user.get("rol", "Admin"),
                "type": "user"
            }
        
        # ✅ Si no se encuentra en users, buscar en drivers (por username)
        driver = await drivers_collection.find_one({"username": identifier})
        
        if driver:
            return {
                "id": str(driver["_id"]),
                "name": driver.get("name"),
                "username": driver.get("username"),
                "rol": driver.get("rol", "Driver"),
                "type": "driver"
            }
        
        # Si no se encuentra en ninguna colección
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}"
        )