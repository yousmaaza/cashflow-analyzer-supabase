from dataclasses import dataclass
from typing import Optional
from datetime import date
from decimal import Decimal

@dataclass
class Transaction:
    date: date
    description: str
    amount: Decimal
    type: str
    raw_text: str = ""

    @classmethod
    def from_line_data(cls, line_data: dict, current_date: Optional[date] = None):
        """Create a transaction from OCR line data"""
        return cls(
            date=current_date or date.today(),
            description=line_data.get('description', ''),
            amount=Decimal(str(line_data.get('amount', 0))),
            type='DEBIT' if line_data.get('amount', 0) < 0 else 'CREDIT',
            raw_text=' '.join(w['text'] for w in line_data.get('words', []))
        )

@dataclass
class ProcessedDocument:
    transactions: List[Transaction]
    page_count: int
    filename: str
    processing_time: float
    error: Optional[str] = None