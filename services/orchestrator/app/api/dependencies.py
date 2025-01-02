from typing import Optional
from fastapi import Header, HTTPException, Depends
from app.core.config import ServiceConfig
from app.core.logger import log

async def verify_api_key(x_api_key: str = Header(...)):
    """Vérifie la clé API dans le header"""
    config = ServiceConfig()
    if x_api_key != config.api.api_key:
        log.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return x_api_key

async def get_user_id(
    x_user_id: Optional[str] = Header(None),
    x_api_key: str = Depends(verify_api_key)
) -> str:
    """Récupère et valide l'ID utilisateur"""
    if not x_user_id:
        raise HTTPException(
            status_code=400,
            detail="X-User-ID header is required"
        )
    return x_user_id

async def validate_workflow_access(
    workflow_id: str,
    user_id: str = Depends(get_user_id),
    config: ServiceConfig = Depends()
) -> bool:
    """Vérifie que l'utilisateur a accès au workflow"""
    # Implémenter la vérification d'accès
    # Pour l'instant, retourne True
    return True