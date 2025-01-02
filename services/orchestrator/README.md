# Cashflow Workflow Orchestrator

## 🏗️ Architecture du Projet

```
workflow-orchestrator/
│
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # Points d'entrée API
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration du service
│   │   └── logger.py          # Configuration du logging
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── document_processor_client.py
│   │   └── transaction_analyzer_client.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── workflow_service.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   │
│   └── orchestration/
│       ├── __init__.py
│       └── pipeline.py        # Définition des pipelines ZenML
│
├── tests/
│   ├── __init__.py
│   └── test_workflow.py
│
├── config/
│   ├── zenml_config.yaml
│   └── service_config.yaml
│
├── pyproject.toml             # Configuration Poetry
├── poetry.lock                # Verrou des dépendances
└── README.md                  # Documentation du projet
```

## 🛠 Prérequis

- Python 3.10+
- Poetry
- Docker (optionnel)

## 📦 Installation

### 1. Cloner le Repository

```bash
git clone <url-du-repository>
cd workflow-orchestrator
```

### 2. Installer Poetry

```bash
# Installer Poetry (si ce n'est pas déjà fait)
pip install poetry

# Configurer Poetry pour créer des environnements virtuels dans le projet
poetry config virtualenvs.in-project true
```

### 3. Installer les Dépendances

```bash
# Installer toutes les dépendances (production et développement)
poetry install

# Activer l'environnement virtuel
poetry shell
```

## 🚀 Démarrage du Service

### Développement

```bash
# Démarrer le serveur de développement
poetry run start
```

### Production

```bash
# Construire l'image Docker
docker build -t workflow-orchestrator .

# Exécuter le conteneur
docker run -p 8000:8000 workflow-orchestrator
```

## 🧪 Tests

```bash
# Exécuter tous les tests
poetry run pytest

# Tests avec couverture de code
poetry run pytest --cov=app
```

## 📝 Utilisation du Workflow

### Configuration

1. Configurer les variables d'environnement dans `.env`
2. Ajuster `config/zenml_config.yaml`

### Exemple de Code

```python
from app.core.config import ServiceConfig
from app.orchestration.pipeline import WorkflowOrchestrator

# Initialisation
config = ServiceConfig()
orchestrator = WorkflowOrchestrator(config)

# Exécution du workflow
result = orchestrator.execute_workflow(
    user_id="user123", 
    document_path="/path/to/document.pdf"
)
```

## 🛠 Développement

### Outils de Qualité de Code

```bash
# Formater le code
poetry run black .

# Vérifier le style
poetry run flake8 .

# Organiser les imports
poetry run isort .
```

## 🔍 Debugging

- Consultez les logs dans `logs/`
- Utilisez le mode debug dans `config/zenml_config.yaml`

## 🤝 Contribution

1. Forker le projet
2. Créer une branche de fonctionnalité
3. Soumettre une Pull Request

### Guidelines

- Suivre les conventions de nommage
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation

## 📄 Licence

[À DÉFINIR]
```

