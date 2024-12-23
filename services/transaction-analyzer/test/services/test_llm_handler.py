import pytest
from datetime import date
import os
import sys
# Add the root directory of the project to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


from app.core.config import ServiceConfig
from app.models.schemas import Transaction
from app.services.llm_handler import LLMHandler

@pytest.fixture
def sample_transactions():
    return [
        Transaction(
            id="1",
            date=date(2023, 10, 1),
            description="Grocery Store",
            amount=150.00,
            raw_text="Grocery Store purchase"
        ),
        Transaction(
            id="2",
            date=date(2023, 10, 2),
            description="Online Subscription",
            amount=9.5,
            raw_text="Monthly subscription"
        )
    ]

@pytest.fixture
def llm_handler():
    config = ServiceConfig()
    return LLMHandler(config)

def test_analyze_transactions(llm_handler, sample_transactions):
    response = llm_handler.analyze_transactions(sample_transactions)
    json_output = response.model_dump_json()
    assert isinstance(json_output, str)
    assert '"id":"1"' in json_output
    assert '"id":"2"' in json_output
    assert '"category":"Groceries"' in json_output
    assert '"category":"Subscriptions"' in json_output
