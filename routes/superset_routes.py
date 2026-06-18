from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os

# Creamos el router
router = APIRouter()

# ⚠️ IMPORTANTE: Cambia estos valores por tu IP/Dominio y credenciales reales
SUPERSET_URL = "https://supersetreports.acedisposal.it.com"  # O "http://localhost:8088" si corren en el mismo server
SUPERSET_API_USER = "api_embed_user"
SUPERSET_API_PASSWORD = "1kVYzT15cENWHdPFssWH"

class TokenResponse(BaseModel):
    token: str

@router.post("/token", response_model=TokenResponse)
async def get_superset_guest_token(dashboard_id: str):
    """
    Endpoint que actúa como puente para autenticarse en Superset
    y generar un Guest Token seguro para el frontend en Vue.
    """
    async with httpx.AsyncClient() as client:
        # 1. Obtener el Access Token de Administrador de API
        login_url = f"{SUPERSET_URL}/api/v1/security/login"
        login_payload = {
            "username": SUPERSET_API_USER,
            "password": SUPERSET_API_PASSWORD,
            "provider": "db"
        }
        
        try:
            login_response = await client.post(login_url, json=login_payload, timeout=10.0)
            if login_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Fallo la autenticación interna con el servidor de reportes."
                )
            
            access_token = login_response.json().get("access_token")
            
            # 2. Solicitar el Guest Token
            guest_token_url = f"{SUPERSET_URL}/api/v1/security/guest_token/"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            guest_payload = {
                "user": {
                    "username": "guest_viewer",
                    "first_name": "Viewer",
                    "last_name": "Logistics"
                },
                "resources": [
                    {
                        "type": "dashboard",
                        "id": dashboard_id
                    }
                ],
                "rls": [] 
            }
            
            guest_response = await client.post(guest_token_url, json=guest_payload, headers=headers, timeout=10.0)
            if guest_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo generar el token de invitado desde Superset."
                )
                
            return TokenResponse(token=guest_response.json().get("token"))
            
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error de conexión con Superset: {exc}"
            )