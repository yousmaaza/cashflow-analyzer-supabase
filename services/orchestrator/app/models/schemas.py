from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class WorkflowState(str, Enum):
    PENDING = "pending"
    DOCUMENT_PROCESSING = "document_processing"
    TRANSACTION_ANALYSIS = "transaction_analysis"
    STORAGE = "storage"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentProcessingResult(BaseModel):
    page_count: int
    processing_time: float
    transactions: List[Dict]
    error: Optional[str] = None

class TransactionAnalysisResult(BaseModel):
    processing_time: float
    transactions: List[Dict]
    error: Optional[str] = None

class WorkflowBase(BaseModel):
    user_id: str
    document_path: str

class WorkflowCreate(WorkflowBase):
    pass

class Workflow(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    state: WorkflowState = WorkflowState.PENDING
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
    results: Dict = Field(default_factory=dict)
    retries: int = 0
    last_retry_at: Optional[datetime] = None

class WorkflowStatus(BaseModel):
    id: str
    state: WorkflowState
    error: Optional[str] = None
    progress: Optional[float] = None
    message: Optional[str] = None

class WorkflowUpdate(BaseModel):
    state: Optional[WorkflowState] = None
    error: Optional[str] = None
    results: Optional[Dict] = None
    retries: Optional[int] = None
    last_retry_at: Optional[datetime] = None