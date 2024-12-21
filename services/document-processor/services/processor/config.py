from dataclasses import dataclass
from typing import List

@dataclass
class ProcessorConfig:
    # Paramètres d'extraction
    min_confidence: float = 0.5
    date_formats: List[str] = None
    
    def __post_init__(self):
        if self.date_formats is None:
            self.date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']