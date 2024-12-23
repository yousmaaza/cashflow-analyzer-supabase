from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Any

class RecurrenceInfo(BaseModel):
    is_recurring: bool = False
    frequency: Optional[str] = None
    typical_amount: Optional[float] = None
    typical_day: Optional[int] = None
    last_occurrence: Optional[date] = None
    next_expected: Optional[date] = None
    variance_amount: Optional[Decimal] = None
    confidence_score: float = 0.0

class Transaction(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    date: date
    description: str
    amount: float
    category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence_score: float = 0.0
    tags: List[str] = Field(default_factory=list)
    raw_text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    recurrence: Optional[RecurrenceInfo] = None

class CategoryPattern(BaseModel):
    pattern: str
    merchant: str = ""
    category: str = ""
    subcategories: List[str]
    frequency: str = ""
    confidence: float = -1
    last_updated: date
    times_used: int = 0
    user_validated: bool = False
    is_recurring: bool = False

class CategorySuggestion(BaseModel):
    category: str = ""
    confidence_score: float = -1
    explanation: str = ""
    similar_transactions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CategorizationRequest(BaseModel):
    transactions: List[Transaction]
    user_id: str
    preferences: Optional[dict] = None

class CategorizationResult(BaseModel):
    transaction: Transaction
    suggested_categories: List[CategorySuggestion]
    patterns_found: List[CategoryPattern]

class BatchCategorizationResponse(BaseModel):
    transactions: List[Transaction]
    processing_time: float
    patterns: List[CategoryPattern]
    new_categories_found: List[str] = Field(default_factory=list)
    recurring_transactions_found: List[str] = Field(default_factory=list)
    error: Optional[str] = None
