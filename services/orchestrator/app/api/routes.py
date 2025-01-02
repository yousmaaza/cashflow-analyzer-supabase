from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.config import ServiceConfig
from app.core.logger import log
from app.models.schemas import (
    WorkflowBase,
    WorkflowCreate,
    WorkflowStatus,

)
from app.models.responses import WorkflowResponse, WorkflowListResponse, ErrorResponse

from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/api/v1")

def get_workflow_service():
    config = ServiceConfig()
    return WorkflowService(config)

@router.post("/workflow", response_model=WorkflowResponse)
async def create_workflow(
    user_id: str,
    background_tasks: BackgroundTasks,
    document: UploadFile = File(...),
    service: WorkflowService = Depends(get_workflow_service)
) -> WorkflowResponse:
    """Crée un nouveau workflow de traitement de document"""
    try:
        log.info(f"Creating workflow for user {user_id} with document {document.filename}")
        
        # Save document to temp directory
        document_path = f"temp/{document.filename}"
        with open(document_path, "wb") as temp_file:
            content = await document.read()
            temp_file.write(content)

        # Create workflow
        workflow = await service.start_workflow(
            WorkflowBase(user_id=user_id, document_path=document_path)
        )

        return WorkflowResponse(
            workflow_id=workflow.id,
            message="Workflow started successfully",
            state=workflow.state
        )

    except Exception as e:
        log.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/{workflow_id}", response_model=WorkflowStatus)
async def get_workflow_status(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service)
) -> WorkflowStatus:
    """Récupère le statut d'un workflow"""
    try:
        workflow = await service.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        progress = None
        if workflow.state in ['document_processing', 'transaction_analysis']:
            # Calculate progress based on steps completed
            progress = service.calculate_workflow_progress(workflow)

        return WorkflowStatus(
            id=workflow.id,
            state=workflow.state,
            error=workflow.error,
            progress=progress,
            message=service.get_status_message(workflow)
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        log.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows", response_model=WorkflowListResponse)
async def list_workflows(
    user_id: str,
    page: int = 1,
    page_size: int = 10,
    state: Optional[str] = None,
    service: WorkflowService = Depends(get_workflow_service)
) -> WorkflowListResponse:
    """Liste les workflows d'un utilisateur"""
    try:
        offset = (page - 1) * page_size
        workflows = await service.get_user_workflows(
            user_id=user_id,
            limit=page_size,
            offset=offset,
            state=state
        )

        return WorkflowListResponse(
            workflows=[WorkflowResponse(
                workflow_id=w.id,
                message=service.get_status_message(w),
                state=w.state
            ) for w in workflows],
            total=len(workflows),
            page=page,
            page_size=page_size
        )

    except Exception as e:
        log.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/{workflow_id}/retry", response_model=WorkflowResponse)
async def retry_workflow(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service)
) -> WorkflowResponse:
    """Retente un workflow échoué"""
    try:
        workflow = await service.retry_workflow(workflow_id)
        if not workflow:
            raise HTTPException(
                status_code=400,
                detail="Workflow cannot be retried"
            )

        return WorkflowResponse(
            workflow_id=workflow.id,
            message="Workflow retry started",
            state=workflow.state
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        log.error(f"Error retrying workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(
    service: WorkflowService = Depends(get_workflow_service)
) -> dict:
    """Vérifie l'état de santé du service et de ses dépendances"""
    try:
        status = await service.check_health()
        if not status['healthy']:
            return JSONResponse(
                status_code=503,
                content=status
            )
        return status

    except Exception as e:
        log.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "healthy": False,
                "error": str(e)
            }
        )