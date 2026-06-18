from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os

# Creamos el router
router = APIRouter()

# ⚠️ Recomendado: mover esto a variables de entorno (.env)
SUPERSET_URL = os.getenv("SUPERSET_URL", "https://supersetreports.acedisposal.it.com")
SUPERSET_API_USER = os.getenv("SUPERSET_API_USER", "api_embed_user")
SUPERSET_API_PASSWORD = os.getenv("SUPERSET_API_PASSWORD", "1kVYzT15cENWHdPFssWH")


class TokenResponse(BaseModel):
    token: str


@router.post("/token", response_model=TokenResponse)
async def get_superset_guest_token(dashboard_id: str):
    """
    Endpoint que actúa como puente para autenticarse en Superset
    y generar un Guest Token seguro para el frontend en Vue.

    Flujo completo requerido por Superset:
      1. Login -> access_token (JWT)
      2. CSRF token (necesario porque WTF_CSRF_ENABLED=True por defecto)
      3. Guest token, enviando el CSRF token + cookie de sesión obtenida en el paso 2
    """
    async with httpx.AsyncClient() as client:
        try:
            # 1. Obtener el Access Token de Administrador de API
            login_url = f"{SUPERSET_URL}/api/v1/security/login"
            login_payload = {
                "username": SUPERSET_API_USER,
                "password": SUPERSET_API_PASSWORD,
                "provider": "db",
                "refresh": True,
            }

            login_response = await client.post(login_url, json=login_payload, timeout=10.0)
            if login_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Fallo la autenticación interna con el servidor de reportes: {login_response.text}",
                )

            access_token = login_response.json().get("access_token")
            auth_headers = {"Authorization": f"Bearer {access_token}"}

            # 2. Obtener el CSRF Token (paso que faltaba)
            csrf_url = f"{SUPERSET_URL}/api/v1/security/csrf_token/"
            csrf_response = await client.get(csrf_url, headers=auth_headers, timeout=10.0)

            if csrf_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"No se pudo obtener el CSRF token de Superset: {csrf_response.text}",
                )

            csrf_token = csrf_response.json().get("result")

            # 3. Solicitar el Guest Token, incluyendo CSRF token + cookies de sesión
            guest_token_url = f"{SUPERSET_URL}/api/v1/security/guest_token/"
            guest_headers = {
                **auth_headers,
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token,
                "Referer": SUPERSET_URL,
            }

            guest_payload = {
                "user": {
                    "username": "guest_viewer",
                    "first_name": "Viewer",
                    "last_name": "Logistics",
                },
                "resources": [
                    {
                        "type": "dashboard",
                        "id": dashboard_id,
                    }
                ],
                "rls": [],
            }

            guest_response = await client.post(
                guest_token_url,
                json=guest_payload,
                headers=guest_headers,
                cookies=csrf_response.cookies,  # <- clave: la cookie de sesión del paso 2
                timeout=10.0,
            )

            if guest_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"No se pudo generar el token de invitado desde Superset: {guest_response.text}",
                )

            return TokenResponse(token=guest_response.json().get("token"))

        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error de conexión con Superset: {exc}",
            )