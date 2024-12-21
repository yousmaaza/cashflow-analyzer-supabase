from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ProcessorConfig:
    # Configuration des types de transactions
    transaction_types: Dict[str, List[str]] = None
    
    # Paramètres d'extraction
    min_confidence: float = 0.5
    date_formats: List[str] = None
    
    def __post_init__(self):
        if self.transaction_types is None:
            self.transaction_types = {
                'DEBIT': ['RETRAIT', 'PAIEMENT', 'VIREMENT EMIS'],
                'CREDIT': ['DEPOT', 'VIREMENT RECU']
            }
        
        if self.date_formats is None:
            self.date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']
