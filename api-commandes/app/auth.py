from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
import os

API_KEY = os.getenv("API_KEY", "dev-key-change-in-prod")
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Vérifie que le header X-API-Key est présent et valide."""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key manquante"
        )
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key invalide"
        )
    return api_key
