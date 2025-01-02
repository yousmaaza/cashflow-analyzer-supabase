import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch

from app.services.transaction_client import TransactionAnalyzerClient
from app.models.schemas import TransactionAnalysisResult

pytest_plugins = ['pytest_asyncio']

@pytest.fixture
def mock_httpx_client():
    with patch('httpx.AsyncClient') as mock_client:
        client_instance = Mock()
        mock_client.return_value = client_instance
        yield client_instance

@pytest.fixture
def transaction_client(test_config):
    return TransactionAnalyzerClient(test_config)

@pytest.mark.asyncio
async def test_analyze_transactions_success(transaction_client, mock_httpx_client):
    # Arrange
    user_id = "test-user"
    transactions = [
        {"id": 1, "amount": 100},
        {"id": 2, "amount": 200}
    ]
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'processing_time': 0.5,
        'transactions': [
            {"id": 1, "amount": 100, "category": "groceries"},
            {"id": 2, "amount": 200, "category": "transport"}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_httpx_client.post = AsyncMock(return_value=mock_response)

    # Act
    result = await transaction_client.analyze_transactions(user_id, transactions)

    # Assert
    assert isinstance(result, TransactionAnalysisResult)
    assert result.processing_time == 0.5
    assert len(result.transactions) == 2
    assert result.transactions[0]['category'] == 'groceries'
    assert not result.error
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_transactions_http_error(transaction_client, mock_httpx_client):
    # Arrange
    user_id = "test-user"
    transactions = [{"id": 1, "amount": 100}]
    mock_httpx_client.post = AsyncMock(
        side_effect=httpx.HTTPError("Error analyzing transactions")
    )

    # Act & Assert
    with pytest.raises(httpx.HTTPError):
        await transaction_client.analyze_transactions(user_id, transactions)

@pytest.mark.asyncio
async def test_batch_analyze_transactions_success(transaction_client, mock_httpx_client):
    # Arrange
    user_id = "test-user"
    transaction_batches = [
        [{"id": 1, "amount": 100}],
        [{"id": 2, "amount": 200}]
    ]

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'processing_time': 0.3,
        'transactions': [{"id": 1, "amount": 100, "category": "groceries"}]
    }
    mock_response.raise_for_status = Mock()
    mock_httpx_client.post = AsyncMock(return_value=mock_response)

    # Act
    results = await transaction_client.batch_analyze_transactions(user_id, transaction_batches)

    # Assert
    assert len(results) == 2
    assert all(isinstance(r, TransactionAnalysisResult) for r in results)
    mock_httpx_client.post.call_count == 2

@pytest.mark.asyncio
async def test_analyze_transactions_invalid_response(transaction_client, mock_httpx_client):
    # Arrange
    user_id = "test-user"
    transactions = [{"id": 1, "amount": 100}]
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.raise_for_status = Mock()
    mock_httpx_client.post = AsyncMock(return_value=mock_response)

    # Act
    result = await transaction_client.analyze_transactions(user_id, transactions)

    # Assert
    assert isinstance(result, TransactionAnalysisResult)
    assert result.processing_time == 0.0
    assert result.transactions == []

@pytest.mark.asyncio
async def test_analyze_transactions_with_empty_list(transaction_client, mock_httpx_client):
    # Arrange
    user_id = "test-user"
    transactions = []

    # Act
    result = await transaction_client.analyze_transactions(user_id, transactions)

    # Assert
    assert isinstance(result, TransactionAnalysisResult)
    assert result.transactions == []
    mock_httpx_client.post.assert_not_called()

@pytest.mark.asyncio
async def test_check_health_success(transaction_client, mock_httpx_client):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'ok'}
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    # Act
    result = await transaction_client.check_health()

    # Assert
    assert result['status'] == 'healthy'
    assert 'latency' in result
    assert result['details'] == {'status': 'ok'}

@pytest.mark.asyncio
async def test_check_health_error(transaction_client, mock_httpx_client):
    # Arrange
    mock_httpx_client.get = AsyncMock(
        side_effect=Exception("Health check failed")
    )

    # Act
    result = await transaction_client.check_health()

    # Assert
    assert result['status'] == 'unhealthy'
    assert 'error' in result

@pytest.mark.asyncio
async def test_retry_mechanism(transaction_client, mock_httpx_client):
    # Arrange
    user_id = "test-user"
    transactions = [{"id": 1, "amount": 100}]
    
    # Mock first two calls to fail, third to succeed
    mock_success_response = Mock()
    mock_success_response.status_code = 200
    mock_success_response.json.return_value = {
        'processing_time': 0.5,
        'transactions': [{"id": 1, "amount": 100, "category": "groceries"}]
    }
    mock_success_response.raise_for_status = Mock()
    
    mock_httpx_client.post = AsyncMock(
        side_effect=[
            httpx.HTTPError("Error 1"),
            httpx.HTTPError("Error 2"),
            mock_success_response
        ]
    )

    # Act
    result = await transaction_client.analyze_transactions(user_id, transactions)

    # Assert
    assert isinstance(result, TransactionAnalysisResult)
    assert not result.error
    assert mock_httpx_client.post.call_count >= 3