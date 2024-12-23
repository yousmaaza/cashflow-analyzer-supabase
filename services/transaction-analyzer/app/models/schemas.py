from typing import List, Optional, Dict
from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from typing import Any

class Transaction(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    date: date
    description: str
    amount: float
    category: Optional[str] = None
    confidence_score: float = 0.0
    raw_text: str = ""

class CategorizationRequest(BaseModel):
    transactions: List[Transaction]
    user_id: str
    preferences: Optional[dict] = None  # Gardé pour compatibilité future

class BatchCategorizationResponse(BaseModel):
    transactions: List[Transaction]
    processing_time: float
    error: Optional[str] = None