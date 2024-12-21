from datetime import datetime
from typing import List, Optional, Dict
from .models import Transaction
from .config import ProcessorConfig

class TransactionExtractor:
    def __init__(self, config: ProcessorConfig):
        self.config = config
        
    def extract_transactions(self, lines: List[Dict], page_num: int) -> List[Transaction]:
        """Extract transactions from OCR lines"""
        transactions = []
        current_date = None

        for line in lines:
            # Vérifier si la ligne contient une date
            potential_date = self._extract_date(line)
            if potential_date:
                current_date = potential_date

            # Extraire la transaction si la ligne en contient une
            transaction = self._extract_transaction(line, current_date)
            if transaction:
                transactions.append(transaction)

        return transactions

    def _extract_date(self, line: Dict) -> Optional[datetime]:
        """Extract date from line if present"""
        text = ' '.join(word['text'] for word in line['words'])
        
        for date_format in self.config.date_formats:
            try:
                return datetime.strptime(text.strip(), date_format).date()
            except ValueError:
                continue
        return None

    def _extract_transaction(self, line: Dict, current_date: datetime) -> Optional[Transaction]:
        """Extract transaction from line if it contains one"""
        if not self._is_transaction_line(line):
            return None
            
        return Transaction.from_line_data({
            'words': line['words'],
            'current_date': current_date
        })