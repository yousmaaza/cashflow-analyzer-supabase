import httpx
from typing import Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import ServiceConfig
from app.core.logger import log
from app.models.schemas import DocumentProcessingResult

class DocumentProcessorClient:
    def __init__(self, config: ServiceConfig):
        """Initialize document processor client

        Args:
            config: Service configuration
        """
        self.config = config
        self.base_url = config.services.document_processor.url
        self.timeout = httpx.Timeout(config.services.document_processor.timeout)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def process_document(self, document_path: str) -> DocumentProcessingResult:
        """Process a document using document processor service

        Args:
            document_path: Path to the document to process

        Returns:
            DocumentProcessingResult with processing results

        Raises:
            httpx.HTTPError: If request fails
        """
        endpoint = f"{self.base_url}{self.config.services.document_processor.endpoints.process}"
        
        try:
            log.info(f"Sending document {document_path} to document processor")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare file for upload
                with open(document_path, 'rb') as f:
                    files = {'file': ('document.pdf', f, 'application/pdf')}
                    response = await client.post(endpoint, files=files)
                response.raise_for_status()

            result = response.json()
            log.info(f"Document processed successfully: {result}")
            
            return DocumentProcessingResult(
                page_count=result.get('page_count', 0),
                processing_time=result.get('processing_time', 0.0),
                transactions=result.get('transactions', []),
                error=result.get('error')
            )

        except httpx.HTTPError as e:
            log.error(f"Error processing document: {str(e)}")
            # Let retry mechanism handle the error
            raise

        except Exception as e:
            log.error(f"Unexpected error processing document: {str(e)}")
            return DocumentProcessingResult(
                page_count=0,
                processing_time=0.0,
                transactions=[],
                error=str(e)
            )

    async def get_status(self, document_id: str) -> Dict:
        """Get status of document processing

        Args:
            document_id: ID of the document

        Returns:
            Dict with status information
        """
        endpoint = f"{self.base_url}{self.config.services.document_processor.endpoints.status}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{endpoint}/{document_id}")
                response.raise_for_status()
                return response.json()

        except Exception as e:
            log.error(f"Error getting document status: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def check_health(self) -> Dict:
        """Check health of document processor service

        Returns:
            Dict with health status
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                start_time = httpx.get_timer()
                response = await client.get(f"{self.base_url}/health")
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