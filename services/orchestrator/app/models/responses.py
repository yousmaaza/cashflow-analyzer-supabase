from typing import List, Optional
from pydantic import BaseModel
from .schemas import WorkflowState

class WorkflowResponse(BaseModel):
    """Response model for workflow operations"""
    workflow_id: str
    message: str
    state: WorkflowState

class WorkflowListResponse(BaseModel):
    """Response model for listing workflows"""
    workflows: List[WorkflowResponse]
    total: int
    page: int
    page_size: int

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    detail: Optional[str] = None
    workflow_id: Optional[str] = None

class WorkflowProgressResponse(BaseModel):
    """Response model for workflow progress"""
    workflow_id: str
    state: WorkflowState
    progress: float
    message: str
    error: Optional[str] = None
    remaining_time: Optional[int] = None  # estimated seconds remaining

class ServiceHealthResponse(BaseModel):
    """Response model for service health checks"""
    service: str
    status: str
    latency: float  # milliseconds
    last_check: str  # ISO format datetime