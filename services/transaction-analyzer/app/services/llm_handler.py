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
        return f"""Vous êtes un analyste de transactions financières. Analysez ces {len(transactions)} transactions pour :
        1. Identifier et catégoriser chaque transaction
        2. Détecter les modèles récurrents et les abonnements
        3. Regrouper les transactions similaires
        4. Extraire les informations sur les commerçants
        
        Pour chaque transaction, fournissez :
        1. Une catégorie suggérée en considérant la description et le montant
        2. S'il s'agit d'une transaction récurrente
        3. Un score de confiance (0-1)
        4. Les étiquettes pertinentes
        La réponse doit être formatée en JSON. et les valeurs doivent être seuelment en français pas d'anglais. 
        Formatez votre réponse en JSON avec cette structure :
        {{
            "transactions": [
                {{
                    "id": "identifiant_transaction",
                    "category": "catégorie_suggérée",
                    "subcategory": "type_spécifique",
                    "confidence": 0.95,
                    "explanation": "raison_de_la_catégorisation",
                    "tags": ["étiquette1", "étiquette2"],
                    "recurrence": {{
                        "is_recurring": true/false,
                        "frequency": "mensuel/hebdomadaire/annuel",
                        "typical_day": jour_du_mois,
                        "confidence": 0.9
                    }}
                }}
            ],
            "patterns": [
                {{
                    "pattern": "description_du_modèle",
                    "merchant": "nom_du_commerçant",
                    "category": "catégorie",
                    "frequency": "mensuel/hebdomadaire/annuel",
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

