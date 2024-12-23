from typing import Dict, List, Optional, Tuple
import json
import tiktoken
from datetime import datetime, date
import calendar
import ollama
from app.core.config import ServiceConfig
from app.models.schemas import (
    Transaction,
    CategorySuggestion,
    CategoryPattern,
    RecurrenceInfo,
    BatchCategorizationResponse
)
from app.core.logger import log
import asyncio


class LLMHandler:
    def __init__(self, config: ServiceConfig):
        """Initialize LLM Handler with Llama 3"""
        self.config = config
        self.model = self.config.get_llm_config()["model_name"]  # Directly use model name
        self.encoding = tiktoken.encoding_for_model("gpt-4")  # Compatible encoding

    def _estimate_tokens(self, text: str) -> int:
        """Estimate number of tokens in text"""
        return len(self.encoding.encode(text))

    def _build_system_prompt(self, transactions: List[Transaction]) -> str:
        """Build system prompt for transaction analysis"""
        return f"""You are a financial transaction analyzer. Analyze these {len(transactions)} transactions to:
                1. Identify and categorize each transaction
                2. Detect recurring patterns and subscriptions
                3. Group similar transactions
                4. Extract merchant information
                
                For each transaction, provide:
                1. A suggested category considering the description and amount
                2. Whether it's a recurring transaction
                3. A confidence score (0-1)
                4. Any relevant tags
                
                Format your response as a JSON with this structure:
                {{
                    "transactions": [
                        {{
                            "id": "transaction_id",
                            "category": "suggested_category",
                            "subcategory": "specific_type",
                            "confidence": 0.95,
                            "explanation": "reason for categorization",
                            "tags": ["tag1", "tag2"],
                            "recurrence": {{
                                "is_recurring": true/false,
                                "frequency": "monthly/weekly/yearly",
                                "typical_day": day of the month,
                                "confidence": 0.9
                            }}
                        }}
                    ],
                    "patterns": [
                        {{
                            "pattern": "pattern description",
                            "merchant": "merchant name",
                            "category": "category",
                            "frequency": "monthly/weekly/yearly",
                            "confidence": 0.9
                        }}
                    ]
                }}"""

    def _build_transaction_prompt(self, transactions: List[Transaction]) -> str:
        """Format transactions for the prompt"""
        transactions_text = []
        for t in transactions:
            transaction_str = f"""ID: {t.id}
                                Date: {t.date}
                                Description: {t.description}
                                Amount: {t.amount}
                                Previous category: {t.category if t.category else 'None'}
                                Raw text: {t.raw_text}
                                ---"""
            transactions_text.append(transaction_str)
        return "\n".join(transactions_text)

    def analyze_transactions(self,
                                   transactions: List[Transaction]) -> BatchCategorizationResponse:
        """Analyze transactions using Llama 3"""
        try:
            # Build prompts
            system_prompt = self._build_system_prompt(transactions)
            transaction_prompt = self._build_transaction_prompt(transactions)

            # Calculate context size
            total_tokens = self._estimate_tokens(system_prompt + transaction_prompt)
            context_size = min(max(4096, total_tokens + 1000), 8192)

            # Get LLM response
            # In 0.1.6, the API might have changed slightly
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Transactions to analyze:\n{transaction_prompt}"}
                ],
                options={
                    "num_ctx": context_size,
                    "temperature": 0.2,
                    "top_p": 0.9
                }
            )
            # log.info(f"Raw LLM response: {response}")
            content = response['message']['content']
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_content = content[json_start:json_end]
            # Parse response
            try:
                # In 0.1.6, the response structure might be different
                results = json.loads(json_content)
                log.info(f"LLM results: {results}")
                return self._process_llm_results(results, transactions)
            except json.JSONDecodeError as e:
                log.error(f"Failed to parse LLM response: {e}")
                return BatchCategorizationResponse(
                    transactions=transactions,
                    processing_time=0,
                    patterns=[],
                    error="Invalid LLM response format"
                )

        except Exception as e:
            log.error(f"Error in transaction analysis: {e}")
            return BatchCategorizationResponse(
                transactions=transactions,
                processing_time=0,
                patterns=[],
                error=str(e)
            )

    def _process_llm_results(self,
                             results: Dict,
                             original_transactions: List[Transaction]) -> BatchCategorizationResponse:
        """Process LLM results and update transactions"""
        # Map original transactions by ID
        transaction_map = {t.id: t for t in original_transactions}
        new_categories = set()
        recurring_transactions = []

        # Process each transaction result
        for result in results.get("transactions", []):

            result["id"] = str(result["id"])

            if result["id"] not in transaction_map.keys():
                continue

            transaction = transaction_map[result["id"]]

            # Update category info
            transaction.category = result["category"]
            transaction.subcategory = result.get("subcategory", "")
            transaction.confidence_score = result["confidence"]
            transaction.tags = result.get("tags", [])

            # Track new categories
            if result["category"] not in new_categories:
                new_categories.add(result["category"])

            # Process recurrence info
            recurrence = result.get("recurrence", {})
            if recurrence.get("is_recurring"):
                recurring_transactions.append(transaction.id)
                transaction.recurrence = RecurrenceInfo(
                    is_recurring=True,
                    frequency=recurrence.get("frequency", ""),
                    typical_day=recurrence.get("typical_day"),
                    confidence_score=recurrence.get("confidence", -1)
                )

        # Create CategoryPatterns from detected patterns
        patterns = [
            CategoryPattern(
                pattern=p["pattern"],
                merchant=p.get("merchant", "") or "",
                category=p["category"],
                subcategories=[],
                frequency=p.get("frequency", "") or "",
                confidence=p["confidence"],
                last_updated=date.today(),
                is_recurring=p.get("frequency", "") != ""
            )
            for p in results.get("patterns", [])
        ]

        return BatchCategorizationResponse(
            transactions=list(transaction_map.values()),
            processing_time=0,  # You might want to track actual processing time
            patterns=patterns,
            new_categories_found=list(new_categories),
            recurring_transactions_found=recurring_transactions
        )
