from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class WorkflowState(str, Enum):
    """États possibles d'un workflow"""
    PENDING = "pending"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class Workflow(BaseModel):
    """
    Modèle représentant un workflow complet
    """
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    document_path: str
    state: WorkflowState = WorkflowState.PENDING

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    document_metadata: Optional[Dict[str, Any]] = None
    analysis_results: Optional[Dict[str, Any]] = None

    error: Optional[str] = None
    retries: int = 0


class WorkflowRequest(BaseModel):
    """Requête de création de workflow"""
    user_id: str
    document_path: str


class WorkflowResponse(BaseModel):
    """Réponse de création de workflow"""
    workflow_id: str
    user_id: str
    status: str
    message: Optional[str] = None


class WorkflowDetailResponse(BaseModel):
    """Détails complets d'un workflow"""
    workflow_id: str
    user_id: str
    status: str
    document_path: str
    created_at: datetime
    updated_at: datetime
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowListResponse(BaseModel):
    """Liste de workflows"""
    workflows: List[WorkflowResponse]
    total: int
    page: int
    page_size: int