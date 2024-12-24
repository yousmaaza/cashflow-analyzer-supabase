from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field

class WorkflowStartRequest(BaseModel):
    """Request model to start a new workflow"""
    user_id: str
    document_path: str
    metadata: Optional[Dict] = Field(default_factory=dict)
    
class WorkflowRetryRequest(BaseModel):
    """Request model to retry a failed workflow"""
    workflow_id: str
    force: bool = False  # Force retry even if max retries reached

class WorkflowListRequest(BaseModel):
    """Request model for listing workflows"""
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    states: Optional[list[str]] = None
    page: int = 1
    page_size: int = 10

class WorkflowCancelRequest(BaseModel):
    """Request model to cancel a workflow"""
    workflow_id: str
    reason: Optional[str] = None