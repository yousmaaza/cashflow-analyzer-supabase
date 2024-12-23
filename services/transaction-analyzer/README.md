# Transaction Analyzer Service

Service d'analyse et de catégorisation des transactions bancaires utilisant Llama 3 et FastAPI.

## 🎯 Fonctionnalités

- Catégorisation automatique des transactions via Llama 3
- Détection des transactions récurrentes
- Identification des patterns de dépenses
- API RESTful avec documentation OpenAPI

## 🛠 Prérequis

- Python 3.10+
- [Ollama](https://ollama.ai/) installé localement
- Llama 3 téléchargé via Ollama

## 🚀 Installation

1. Cloner le repository :
```bash
git clone https://github.com/yousmaaza/cashflow-analyzer-supabase.git
cd services/transaction-analyzer
```

2. Créer un environnement virtuel Python :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Installer et configurer Ollama avec Llama 3 :
```bash
# Installation d'Ollama (voir https://ollama.ai/download)

# Téléchargement du modèle Llama 3
ollama pull llama3

# Configuration du contexte (optionnel)
ollama show --modelfile llama3 > modelfile
# Modifier num_ctx dans le modelfile si nécessaire
ollama create custom-llama3 -f modelfile
```

## 📝 Configuration

1. Créer un fichier `.env` à la racine du projet :
```env
# API Configuration
PORT=8000
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# LLM Configuration
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=llama3
```

## 🏃‍♂️ Lancement du service

1. Démarrer le service en mode développement :
```bash
uvicorn main:app --reload --port 8000
```

2. Accéder à :
   - API Documentation: http://localhost:8000/docs
   - API Alternative Doc: http://localhost:8000/redoc
   - Healthcheck: http://localhost:8000/

## 📊 Test du service

1. Exemple de requête d'analyse de transactions :
```bash
curl -X POST "http://localhost:8000/api/v1/transactions/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "transactions": [
         {
           "id": "tx1",
           "date": "2024-01-15",
           "description": "CARREFOUR MARKET",
           "amount": 42.50,
           "raw_text": "PAIEMENT CB CARREFOUR MARKET"
         }
       ]
     }'
```

## 🧪 Tests

Exécuter les tests unitaires :
```bash
pytest
```

Avec couverture de code :
```bash
pytest --cov=app tests/
```

## 💡 Développement

1. Structure du projet :
```
transaction-analyzer/
├── app/
│   ├── api/              # Routes FastAPI
│   │   ├── __init__.py
│   │   └── routes.py    # Endpoints API
│   ├── core/            # Configuration et utilitaires
│   │   ├── __init__.py
│   │   ├── config.py    # Configuration service
│   │   └── logger.py    # Configuration logging
│   ├── models/          # Modèles de données
│   │   ├── __init__.py
│   │   └── schemas.py   # Schémas Pydantic
│   └── services/        # Logique métier
│       ├── __init__.py
│       ├── llm_handler.py     # Gestion LLM
│       └── transaction_service.py  # Service principal
├── tests/               # Tests unitaires
│   ├── __init__.py
│   ├── conftest.py     # Configuration pytest
│   ├── test_api/       # Tests API
│   │   ├── __init__.py
│   │   └── test_routes.py
│   ├── test_services/  # Tests services
│   │   ├── __init__.py
│   │   ├── test_llm_handler.py
│   │   └── test_transaction_service.py
│   └── test_models/    # Tests modèles
│       ├── __init__.py
│       └── test_schemas.py
├── .env                # Configuration locale
├── .gitignore         # Fichiers ignorés par git
├── main.py            # Point d'entrée de l'application
├── requirements.txt    # Dépendances Python
└── README.md          # Documentation du projet
```

2. Guidelines développement :
- Utiliser Black pour le formatage : `black app/`
- Vérifier le lint : `flake8 app/`
- Organiser les imports : `isort app/`

## 🤝 Contribution

1. Créer une nouvelle branche pour votre fonctionnalité
2. Implémenter vos changements
3. Ajouter des tests
4. Soumettre une Pull Request

## ⚠️ Notes importantes

- Assurez-vous qu'Ollama est en cours d'exécution lors de l'utilisation du service
- Le modèle Llama 3 nécessite environ 4GB de RAM
- Le premier appel à l'API peut être lent dû au chargement initial du modèle