from typing import List
from .models import Transaction
from core.config import ServiceConfig

class TransactionValidator:
    def __init__(self, config: ServiceConfig):
        self.config = config

    def validate_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """Validate and filter transactions

        Args:
            transactions: List of transactions to validate

        Returns:
            Validated transactions
        """
        return [
            transaction for transaction in transactions
            if self._is_valid_transaction(transaction)
        ]

    def _is_valid_transaction(self, transaction: Transaction) -> bool:
        """Check if a transaction is valid

        Args:
            transaction: Transaction to validate

        Returns:
            True if transaction meets validation criteria, False otherwise
        """
        # Vérifier les champs requis
        required_fields_met = all(
            getattr(transaction, field, None) is not None
            for field in self.config.validation.required_fields
        )

        # Vérifier le montant minimum
        amount_valid = abs(transaction.amount) >= self.config.validation.min_transaction_amount

        return required_fields_met and amount_valid