from typing import Dict, List
import json
from datetime import date
import ollama
from app.core.config import ServiceConfig
from app.models.schemas import (
    Transaction,
    BatchCategorizationResponse
)
from app.core.logger import log


class LLMHandler:
    def __init__(self, config: ServiceConfig):
        """Initialize LLM Handler with Llama 3"""
        self.config = config
        self.model = self.config.get_llm_config()["model_name"]

    def _build_system_prompt(self, transactions: List[Transaction]) -> str:
        """Build system prompt for transaction analysis"""
        return f"""Vous êtes un analyste de transactions financières. Analysez ces {len(transactions)} transactions pour les catégoriser.

        Pour chaque transaction, fournissez :
        1. Une catégorie simple en UN SEUL MOT (exemple: Alimentation, Transport, Loisirs)

        Voici des exemples de catégories à utiliser :
        - Alimentation
        - Transport
        - Loisirs
        - Logement
        - Santé
        - Abonnements
        - Shopping
        - Restaurants
        - Voyages
        - Services
        - Education

        Pour chaque transaction, la réponse doit inclure :
        - La catégorie (un seul mot)
        - Un score de confiance (0-1)

        Format attendu du JSON :
        {{
            "transactions": [
                {{
                    "id": "identifiant_transaction",
                    "category": "Alimentation",  # Un seul mot !
                    "confidence": 0.95
                }}
            ]
        }}

        IMPORTANT : Les catégories doivent être en un seul mot, pas de phrases !"""

    def _build_transaction_prompt(self, transactions: List[Transaction]) -> str:
        """Format transactions for the prompt"""
        transactions_text = []
        for t in transactions:
            transaction_str = f"""ID: {t.id}
            Description: {t.description}
            Montant: {t.amount}
            ---"""
            transactions_text.append(transaction_str)
        return "\n".join(transactions_text)

    def analyze_transactions(self, transactions: List[Transaction]) -> BatchCategorizationResponse:
        """Analyze transactions using Llama 3"""
        try:
            # Get LLM response
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._build_system_prompt(transactions)},
                    {"role": "user", "content": self._build_transaction_prompt(transactions)}
                ],
                options={
                    "temperature": 0.2,
                }
            )

            # Extract and parse JSON response
            content = response['message']['content']
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            json_content = content[json_start:json_end]

            results = json.loads(json_content)
            return self._process_llm_results(results, transactions)

        except Exception as e:
            log.error(f"Error in transaction analysis: {e}")
            return BatchCategorizationResponse(
                transactions=transactions,
                processing_time=0,
                error=str(e)
            )

    def _process_llm_results(self, results: Dict,
                             original_transactions: List[Transaction]) -> BatchCategorizationResponse:
        """Process LLM results and update transactions"""
        transaction_map = {t.id: t for t in original_transactions}

        # Update transactions with LLM results
        for result in results.get("transactions", []):
            if str(result["id"]) in transaction_map:
                transaction = transaction_map[str(result["id"])]
                transaction.category = result["category"]
                transaction.confidence_score = result["confidence"]

        return BatchCategorizationResponse(
            transactions=list(transaction_map.values()),
            processing_time=0
        )