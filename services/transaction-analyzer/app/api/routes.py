from fastapi import APIRouter, HTTPException, Depends

from app.core.config import ServiceConfig
from app.models.schemas import (
    CategorizationRequest,
    BatchCategorizationResponse
)
from app.services.transaction_service import TransactionService
from app.core.logger import log

router = APIRouter(
    prefix="/api/v1/transactions",
    tags=["transactions"]
)

def get_transaction_service():
    config = ServiceConfig()
    return TransactionService(config)

@router.post("/analyze", response_model=BatchCategorizationResponse)
def analyze_transactions(
    request: CategorizationRequest,
    service: TransactionService = Depends(get_transaction_service)
) -> BatchCategorizationResponse:
    """
    Analyze a batch of transactions to categorize them and detect patterns

    Args:
        request: CategorizationRequest containing:
            - transactions: List of transactions to analyze
            - user_id: ID of the requesting user
            - preferences: Optional user preferences for categorization

    Returns:
        BatchCategorizationResponse containing:
            - Categorized transactions
            - Detected patterns
            - Processing metadata
    """
    try:
        log.info(f"Received analysis request for user {request.user_id} with {len(request.transactions)} transactions")
        response = service.analyze_transactions(request)

        if response.error:
            raise HTTPException(status_code=500, detail=response.error)

        return response

    except Exception as e:
        log.error(f"Error processing analysis request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))