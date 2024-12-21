from typing import List
from .models import Transaction
from .config import ProcessorConfig

class TransactionValidator:
    def __init__(self, config: ProcessorConfig):
        self.config = config

    def validate_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """Validate and filter transactions"""
        return [t for t in transactions if self._is_valid(t)]

    def _is_valid(self, transaction: Transaction) -> bool:
        """Check if a transaction is valid"""
        return all([
            transaction.amount != 0,
            transaction.description.strip() != '',
            transaction.confidence >= self.config.min_confidence
        ])