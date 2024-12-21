from typing import List
from .models import Transaction
from .config import ProcessorConfig

class TransactionCategorizer:
    def __init__(self, config: ProcessorConfig):
        self.config = config

    def categorize_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """Add categories to transactions"""
        for transaction in transactions:
            transaction.type = self._determine_type(transaction)
            transaction.category = self._determine_category(transaction)
        return transactions

    def _determine_type(self, transaction: Transaction) -> str:
        """Determine transaction type based on description and amount"""
        description = transaction.description.upper()
        
        for type_name, keywords in self.config.transaction_types.items():
            if any(keyword in description for keyword in keywords):
                return type_name
                
        return 'DEBIT' if transaction.amount < 0 else 'CREDIT'

    def _determine_category(self, transaction: Transaction) -> str:
        """Determine transaction category based on description"""
        # Implémenter la logique de catégorisation
        return 'AUTRE'