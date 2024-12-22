import re
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional
import pandas as pd

from core.config import ServiceConfig
from core.logger import log
from .models import Transaction


class TransactionExtractor:
    def __init__(self, config: ServiceConfig):
        """Initialize TransactionExtractor

        Args:
            config: Service configuration object
        """
        self.config = config

    def extract_transactions(self, lines: List[Dict], page_num: int) -> List[Transaction]:
        """Extract transactions from OCR lines

        Args:
            lines: List of OCR processed lines
            page_num: Page number of the document

        Returns:
            List of extracted transactions
        """
        transactions = []
        filename = f"page_{page_num + 1}"

        # Expression régulière modifiée pour détecter une date au début de la ligne
        # Accepte 1-31 pour le jour et 1-12 pour le mois
        date_pattern = r'^(\d{1,2})\.(\d{1,2})'

        for line in lines:
            # Récupérer le texte de la ligne en joignant les mots
            line_text = ' '.join(word['text'] for word in line['words'])

            # Vérifier si la ligne commence par une date
            match = re.match(date_pattern, line_text)
            if match:
                try:
                    # Extraire la date
                    day, month = match.groups()
                    # Ajouter les zéros si nécessaire
                    day = day.zfill(2)
                    month = month.zfill(2)
                    current_year = datetime.now().year
                    transaction_date = datetime.strptime(f"{day}.{month}.{current_year}", "%d.%m.%Y").date()

                    # Extraire le montant (dernier mot de la ligne)
                    amount_str = line['words'][-1]['text'].replace(',', '.')
                    try:
                        amount = float(amount_str)
                    except ValueError:
                        continue

                    # Extraire le libellé (tout ce qui est entre la date et le montant)
                    libelle = ' '.join(word['text'] for word in line['words'][1:-1])

                    # Créer la transaction
                    transaction = Transaction(
                        date=transaction_date,
                        description=libelle,
                        amount=amount,
                        raw_text=' '.join(word['text'] for word in line['words'])
                    )

                    transactions.append(transaction)

                    log.info(f"Transaction trouvée: Date={transaction_date.strftime('%d.%m.%Y')}, "
                             f"Libellé={libelle}, Montant={amount}")

                except (ValueError, IndexError) as e:
                    # log.error(f"Erreur lors du parsing de la ligne: {line_text}")
                    continue

        return transactions



    def to_dataframe(self, transactions: List[Transaction]) -> pd.DataFrame:
        """Convert transactions to pandas DataFrame

        Args:
            transactions: List of Transaction objects

        Returns:
            DataFrame with transaction data
        """
        if not transactions:
            return pd.DataFrame()

        # Convertir les transactions en dictionnaires
        transaction_dicts = [
            {
                'date': t.date,
                'description': t.description,
                'amount': float(t.amount),
                'raw_text': t.raw_text
            } for t in transactions
        ]

        # Créer le DataFrame
        df = pd.DataFrame(transaction_dicts)

        # Formater les colonnes si nécessaire
        df['amount'] = df['amount'].astype(float)

        return df