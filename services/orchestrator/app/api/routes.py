from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.core.config import ServiceConfig
from app.orchestration.pipeline import WorkflowOrchestrator

router = APIRouter()


def get_workflow_service():
    """
    Dépendance pour obtenir le service de workflow
    """
    config = ServiceConfig()
    return WorkflowOrchestrator(config)


@router.post("/workflow")
async def create_workflow(
        user_id: str,
        document_path: str,
        workflow_service: WorkflowOrchestrator = Depends(get_workflow_service)
) -> Dict[str, Any]:
    """
    Lance un nouveau workflow de traitement financier

    Args:
        user_id: Identifiant de l'utilisateur
        document_path: Chemin du document à traiter
        workflow_service: Service de workflow

    Returns:
        Résultats du workflow
    """
    try:
        result = workflow_service.execute_workflow(
            user_id=user_id,
            document_path=document_path
        )
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Vérifie la santé du service
    """
    return {
        "status": "healthy",
        "service": "Workflow Orchestrator"
    }