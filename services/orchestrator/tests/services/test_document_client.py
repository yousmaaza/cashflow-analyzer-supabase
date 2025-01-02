import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path

from app.services.document_client import DocumentProcessorClient
from app.models.schemas import DocumentProcessingResult

pytest_plugins = ['pytest_asyncio']

@pytest.fixture
def mock_httpx_client():
    with patch('httpx.AsyncClient') as mock_client:
        client_instance = Mock()
        mock_client.return_value = client_instance
        yield client_instance

@pytest.fixture
def document_client(test_config):
    return DocumentProcessorClient(test_config)

@pytest.mark.asyncio
async def test_process_document_success(document_client, mock_httpx_client):
    # Arrange
    document_path = "/test/document.pdf"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'page_count': 2,
        'processing_time': 1.5,
        'transactions': [
            {'id': 1, 'amount': 100},
            {'id': 2, 'amount': 200}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_httpx_client.post = AsyncMock(return_value=mock_response)

    # Mock file open
    mock_file = Mock()
    with patch('builtins.open', return_value=mock_file):
        # Act
        result = await document_client.process_document(document_path)

    # Assert
    assert isinstance(result, DocumentProcessingResult)
    assert result.page_count == 2
    assert result.processing_time == 1.5
    assert len(result.transactions) == 2
    assert not result.error
    mock_httpx_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_process_document_http_error(document_client, mock_httpx_client):
    # Arrange
    document_path = "/test/document.pdf"
    mock_httpx_client.post = AsyncMock(
        side_effect=httpx.HTTPError("Error processing document")
    )

    # Mock file open
    mock_file = Mock()
    with patch('builtins.open', return_value=mock_file):
        # Act & Assert
        with pytest.raises(httpx.HTTPError):
            await document_client.process_document(document_path)

@pytest.mark.asyncio
async def test_process_document_invalid_response(document_client, mock_httpx_client):
    # Arrange
    document_path = "/test/document.pdf"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.raise_for_status = Mock()
    mock_httpx_client.post = AsyncMock(return_value=mock_response)

    # Mock file open
    mock_file = Mock()
    with patch('builtins.open', return_value=mock_file):
        # Act
        result = await document_client.process_document(document_path)

    # Assert
    assert isinstance(result, DocumentProcessingResult)
    assert result.page_count == 0
    assert result.transactions == []

@pytest.mark.asyncio
async def test_get_status_success(document_client, mock_httpx_client):
    # Arrange
    document_id = "test-doc-id"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'status': 'completed',
        'progress': 100
    }
    mock_response.raise_for_status = Mock()
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    # Act
    result = await document_client.get_status(document_id)

    # Assert
    assert result['status'] == 'completed'
    assert result['progress'] == 100
    mock_httpx_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_get_status_error(document_client, mock_httpx_client):
    # Arrange
    document_id = "test-doc-id"
    mock_httpx_client.get = AsyncMock(
        side_effect=Exception("Connection error")
    )

    # Act
    result = await document_client.get_status(document_id)

    # Assert
    assert result['status'] == 'error'
    assert 'error' in result

@pytest.mark.asyncio
async def test_check_health_success(document_client, mock_httpx_client):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'ok'}
    mock_httpx_client.get = AsyncMock(return_value=mock_response)

    # Act
    result = await document_client.check_health()

    # Assert
    assert result['status'] == 'healthy'
    assert 'latency' in result
    assert result['details'] == {'status': 'ok'}

@pytest.mark.asyncio
async def test_check_health_error(document_client, mock_httpx_client):
    # Arrange
    mock_httpx_client.get = AsyncMock(
        side_effect=Exception("Health check failed")
    )

    # Act
    result = await document_client.check_health()

    # Assert
    assert result['status'] == 'unhealthy'
    assert 'error' in result