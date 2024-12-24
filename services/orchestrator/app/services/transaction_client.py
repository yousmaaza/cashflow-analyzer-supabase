import httpx
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import ServiceConfig
from app.core.logger import log
from app.models.schemas import TransactionAnalysisResult

class TransactionAnalyzerClient:
    def __init__(self, config: ServiceConfig):
        """Initialize transaction analyzer client

        Args:
            config: Service configuration
        """
        self.config = config
        self.base_url = config.services.transaction_analyzer.url
        self.timeout = httpx.Timeout(config.services.transaction_analyzer.timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def analyze_transactions(self, user_id: str, transactions: List[Dict]) -> TransactionAnalysisResult:
        """Analyze transactions using transaction analyzer service

        Args:
            user_id: ID of the user
            transactions: List of transactions to analyze

        Returns:
            TransactionAnalysisResult with analysis results

        Raises:
            httpx.HTTPError: If request fails
        """
        endpoint = f"{self.base_url}{self.config.services.transaction_analyzer.endpoints.analyze}"

        try:
            log.info(f"Sending {len(transactions)} transactions for analysis")
            
            payload = {
                "user_id": user_id,
                "transactions": transactions
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload)
                response.raise_for_status()

            result = response.json()
            log.info(f"Transactions analyzed successfully")

            return TransactionAnalysisResult(
                processing_time=result.get('processing_time', 0.0),
                transactions=result.get('transactions', []),
                error=result.get('error')
            )

        except httpx.HTTPError as e:
            log.error(f"Error analyzing transactions: {str(e)}")
            raise

        except Exception as e:
            log.error(f"Unexpected error analyzing transactions: {str(e)}")
            return TransactionAnalysisResult(
                processing_time=0.0,
                transactions=[],
                error=str(e)
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def batch_analyze_transactions(self, user_id: str, transaction_batches: List[List[Dict]]) -> List[TransactionAnalysisResult]:
        """Analyze multiple batches of transactions

        Args:
            user_id: ID of the user
            transaction_batches: List of transaction batches

        Returns:
            List of TransactionAnalysisResult, one per batch
        """
        results = []
        for batch in transaction_batches:
            result = await self.analyze_transactions(user_id, batch)
            results.append(result)
        return results

    async def check_health(self) -> Dict:
        """Check health of transaction analyzer service

        Returns:
            Dict with health status
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                start_time = httpx.get_timer()
                response = await client.get(f"{self.base_url}/")
                elapsed = httpx.get_timer() - start_time

                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "latency": elapsed * 1000,  # Convert to milliseconds
                    "details": response.json() if response.status_code == 200 else None
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }