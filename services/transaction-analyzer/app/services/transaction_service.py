from typing import List
import time
from app.core.config import ServiceConfig
from app.core.logger import log
from app.models.schemas import (
    Transaction,
    BatchCategorizationResponse,
    CategorizationRequest
)
from app.services.llm_handler import LLMHandler


class TransactionService:
    def __init__(self, config: ServiceConfig):
        """Initialize Transaction Analysis Service"""
        self.config = config
        self.llm_handler = LLMHandler(config)

    def analyze_transactions(
            self,
            request: CategorizationRequest
    ) -> BatchCategorizationResponse:
        """
        Analyze a batch of transactions
        """
        start_time = time.time()
        log.info(f"Starting transaction analysis for user {request.user_id}")

        try:
            # Pre-process transactions
            preprocessed_transactions = self._preprocess_transactions(request.transactions)

            # Get LLM analysis
            response = self.llm_handler.analyze_transactions(preprocessed_transactions)

            # Calculate processing time
            processing_time = time.time() - start_time
            response.processing_time = processing_time

            log.info(f"Analysis completed in {processing_time:.2f}s")
            return response

        except Exception as e:
            error_msg = f"Error analyzing transactions: {str(e)}"
            log.error(error_msg)
            return BatchCategorizationResponse(
                transactions=request.transactions,
                processing_time=time.time() - start_time,
                error=error_msg
            )

    def _preprocess_transactions(
            self,
            transactions: List[Transaction]
    ) -> List[Transaction]:
        """Simple preprocessing: normalize descriptions"""
        processed = []
        for transaction in transactions:
            processed_tx = Transaction(
                id=transaction.id,
                date=transaction.date,
                description=self._normalize_description(transaction.description),
                amount=transaction.amount,
                raw_text=transaction.raw_text
            )
            processed.append(processed_tx)
        return processed

    def _normalize_description(self, description: str) -> str:
        """Basic description normalization"""
        if not description:
            return ""
        return description.upper()