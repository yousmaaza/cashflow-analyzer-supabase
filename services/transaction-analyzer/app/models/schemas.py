from typing import List, Optional, Dict
from datetime import date, datetime
from decimal import Decimal
from dataclasses import dataclass, field

@dataclass
class RecurrenceInfo:
    is_recurring: bool = False
    frequency: Optional[str] = None       # 'monthly', 'weekly', 'yearly', etc.
    typical_amount: Optional[Decimal] = None
    typical_day: Optional[int] = None     # Jour du mois/semaine habituel
    last_occurrence: Optional[date] = None
    next_expected: Optional[date] = None
    variance_amount: Optional[Decimal] = None  # Variation habituelle du montant
    confidence_score: float = 0.0
    
@dataclass
class Transaction:
    id: str
    date: date
    description: str
    amount: Decimal
    category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    raw_text: str = ""
    metadata: Dict[str, any] = field(default_factory=dict)
    recurrence: Optional[RecurrenceInfo] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": str(self.date),
            "description": self.description,
            "amount": str(self.amount),
            "category": self.category,
            "subcategory": self.subcategory,
            "confidence_score": self.confidence_score,
            "tags": self.tags,
            "raw_text": self.raw_text,
            "metadata": self.metadata,
            "recurrence": {
                "is_recurring": self.recurrence.is_recurring,
                "frequency": self.recurrence.frequency,
                "typical_amount": str(self.recurrence.typical_amount) if self.recurrence.typical_amount else None,
                "typical_day": self.recurrence.typical_day,
                "last_occurrence": str(self.recurrence.last_occurrence) if self.recurrence.last_occurrence else None,
                "next_expected": str(self.recurrence.next_expected) if self.recurrence.next_expected else None,
                "variance_amount": str(self.recurrence.variance_amount) if self.recurrence.variance_amount else None,
                "confidence_score": self.recurrence.confidence_score
            } if self.recurrence else None
        }

@dataclass
class CategoryPattern:
    pattern: str
    merchant: str
    category: str
    subcategories: List[str]
    frequency: str
    confidence: float
    last_updated: date
    times_used: int = 0
    user_validated: bool = False
    is_recurring: bool = False

@dataclass
class CategorySuggestion:
    category: str
    confidence_score: float
    explanation: str
    similar_transactions: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

@dataclass
class CategorizationRequest:
    transactions: List[Transaction]
    user_id: str
    preferences: Optional[dict] = None

@dataclass
class CategorizationResult:
    transaction: Transaction
    suggested_categories: List[CategorySuggestion]
    patterns_found: List[CategoryPattern]
    
@dataclass
class BatchCategorizationResponse:
    transactions: List[Transaction]
    processing_time: float
    patterns: List[CategoryPattern]
    new_categories_found: List[str] = field(default_factory=list)
    recurring_transactions_found: List[str] = field(default_factory=list)  # IDs des transactions récurrentes
    error: Optional[str] = None