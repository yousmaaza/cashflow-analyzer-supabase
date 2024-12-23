from typing import List, Optional, Dict
import time
from datetime import date

from app.core.config import ServiceConfig
from app.core.logger import log
from app.models.schemas import (
    Transaction,
    BatchCategorizationResponse,
    CategoryPattern,
    CategorizationRequest
)
from app.services.llm_handler import LLMHandler
import json
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

        Args:
            request: CategorizationRequest containing transactions and user preferences

        Returns:
            BatchCategorizationResponse with analyzed transactions
        """
        start_time = time.time()
        log.info(f"Starting transaction analysis for user {request.user_id}")

        try:
            # Pre-process transactions
            preprocessed_transactions = self._preprocess_transactions(request.transactions)

            log.info(f"Preprocessed {len(preprocessed_transactions)} transactions")



            # Apply any user preferences/rules
            if request.preferences:
                self._apply_user_preferences(preprocessed_transactions, request.preferences)

            # Get LLM analysis
            log.info("Analyzing transactions with LLM model")
            response = self.llm_handler.analyze_transactions(preprocessed_transactions)
            log.info(f"LLM analysis completed")



            # Post-process results
            final_response = self._postprocess_results(response)

            # Calculate processing time
            processing_time = time.time() - start_time
            final_response.processing_time = processing_time

            log.info(f"""Analysis completed in {processing_time:.2f}s:
                     - Transactions processed: {len(request.transactions)}
                     - New categories found: {len(final_response.new_categories_found)}
                     - Recurring transactions: {len(final_response.recurring_transactions_found)}
                     """)

            final_response_json = final_response.model_dump_json()


            return final_response

        except Exception as e:
            error_msg = f"Error analyzing transactions: {str(e)}"
            log.error(error_msg)
            return BatchCategorizationResponse(
                transactions=request.transactions,
                processing_time=time.time() - start_time,
                patterns=[],
                error=error_msg
            )

    def _preprocess_transactions(
        self,
        transactions: List[Transaction]
    ) -> List[Transaction]:
        """
        Preprocess transactions before analysis

        - Normalize descriptions
        - Sort by date
        - Clean data
        - Apply any known patterns
        """
        processed = []
        for transaction in transactions:
            # Create a copy to avoid modifying original
            processed_tx = Transaction(
                id=transaction.id,
                date=transaction.date,
                description=self._normalize_description(transaction.description),
                amount=transaction.amount,
                category=transaction.category,
                raw_text=transaction.raw_text
            )
            processed.append(processed_tx)

        # Sort by date
        return sorted(processed, key=lambda x: x.date)


    def _normalize_description(self, description: str) -> str:
        """Normalize transaction description"""
        if not description:
            return ""

        # Convert to uppercase for consistency
        normalized = description.upper()
        # Remove special characters
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        return normalized

    def _apply_user_preferences(
        self,
        transactions: List[Transaction],
        preferences: Dict
    ) -> None:
        """Apply user preferences to transactions"""
        if not preferences:
            return

        # Apply category overrides
        category_overrides = preferences.get('category_overrides', {})
        for transaction in transactions:
            normalized_desc = self._normalize_description(transaction.description)
            if normalized_desc in category_overrides:
                transaction.category = category_overrides[normalized_desc]
                transaction.confidence_score = 1.0  # User-defined category

    def _postprocess_results(
        self,
        response: BatchCategorizationResponse
    ) -> BatchCategorizationResponse:
        """
        Post-process analysis results

        - Apply business rules
        - Validate categories
        - Merge similar patterns
        """
        if not response or response.error:
            return response

        # Merge similar patterns
        merged_patterns = self._merge_similar_patterns(response.patterns)

        # Sort transactions by date
        sorted_transactions = sorted(response.transactions, key=lambda x: x.date)

        return BatchCategorizationResponse(
            transactions=sorted_transactions,
            processing_time=response.processing_time,
            patterns=merged_patterns,
            new_categories_found=response.new_categories_found,
            recurring_transactions_found=response.recurring_transactions_found
        )

    def _merge_similar_patterns(
        self,
        patterns: List[CategoryPattern]
    ) -> List[CategoryPattern]:
        """Merge similar transaction patterns"""
        if not patterns:
            return []

        # Group patterns by merchant
        merchant_patterns = {}
        for pattern in patterns:
            if pattern.merchant not in merchant_patterns:
                merchant_patterns[pattern.merchant] = []
            merchant_patterns[pattern.merchant].append(pattern)

        # Merge patterns for same merchant
        merged_patterns = []
        for merchant, merchant_group in merchant_patterns.items():
            if len(merchant_group) == 1:
                merged_patterns.append(merchant_group[0])
                continue

            # Merge patterns with high similarity
            merged = merchant_group[0]
            for pattern in merchant_group[1:]:
                if self._are_patterns_similar(merged, pattern):
                    merged.confidence = max(merged.confidence, pattern.confidence)
                    merged.subcategories.extend(pattern.subcategories)
                    # Keep unique subcategories
                    merged.subcategories = list(set(merged.subcategories))
                else:
                    merged_patterns.append(pattern)

            merged_patterns.append(merged)

        return merged_patterns

    def _are_patterns_similar(
        self,
        pattern1: CategoryPattern,
        pattern2: CategoryPattern
    ) -> bool:
        """Check if two patterns are similar enough to merge"""
        # Same category and frequency
        if pattern1.category != pattern2.category or pattern1.frequency != pattern2.frequency:
            return False

        # Similar merchant names
        if self._calculate_similarity(pattern1.merchant, pattern2.merchant) < 0.8:
            return False

        return True

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple implementation - could be improved with more sophisticated algorithms
        str1 = str1.upper()
        str2 = str2.upper()

        if str1 == str2:
            return 1.0

        # Check if one is substring of other
        if str1 in str2 or str2 in str1:
            return 0.8

        # Could add more sophisticated similarity metrics here
        return 0.0