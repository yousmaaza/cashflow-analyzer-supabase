# Tests de l'Orchestrateur

Ce dossier contient les tests unitaires et d'intégration pour le service d'orchestration.

## 🗂 Structure

```
tests/
├── conftest.py              # Configuration pytest et fixtures
├── test_config.yaml         # Configuration pour les tests
├── services/
│   ├── test_workflow_service.py     # Tests du service principal
│   ├── test_document_client.py      # Tests du client Document Processor
│   ├── test_transaction_client.py   # Tests du client Transaction Analyzer
│   └── test_supabase_client.py      # Tests du client Supabase
└── README.md               # Cette documentation
```

## 🚀 Exécution des tests

### Tests unitaires
```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/services/test_workflow_service.py

# Avec couverture
pytest --cov=app tests/

# Avec rapport détaillé
pytest --cov=app --cov-report=html tests/
```

## 🔧 Configuration

### Fixtures

```python
# Configuration de test
@pytest.fixture
def test_config():
    return ServiceConfig(config_path='tests/test_config.yaml')

# Clients mockés
@pytest.fixture
def mock_document_client(test_config):
    return Mock(spec=DocumentProcessorClient)

@pytest.fixture
def mock_transaction_client(test_config):
    return Mock(spec=TransactionAnalyzerClient)
```

## 📝 Tests par module

### WorkflowService
- Start workflow
- Traitement des documents
- Analyse des transactions
- Gestion des erreurs
- Retries

### DocumentProcessorClient
- Process document
- Health check
- Gestion des erreurs HTTP
- Retry automatique

### TransactionAnalyzerClient
- Analyse simple et par lots
- Validation des résultats
- Health check
- Gestion des timeouts

### SupabaseClient
- CRUD workflows
- Stockage transactions
- Gestion des erreurs
- Row Level Security

## 🛡️ Mocking

### HTTP Requests
```python
@pytest.mark.asyncio
async def test_api_call(mock_httpx_client):
    mock_response = Mock(status_code=200)
    mock_httpx_client.post = AsyncMock(return_value=mock_response)
```

### Base de données
```python
@pytest.fixture
def mock_supabase():
    with patch('app.services.supabase_client.create_client') as mock:
        yield mock.return_value
```

## 🔍 Couverture de tests

### Objectifs
- Code métier : > 90%
- Utilitaires : > 80%
- Total : > 85%

### Exclusions
- Code de configuration
- Logs et métriques
- Scripts de migration

## 🎯 Types de tests

### Tests unitaires
- Isolation complète (mocks)
- Rapides et déterministes
- Un cas de test par scénario

### Tests asynchrones
- Utilisation de pytest-asyncio
- Mocking des appels async
- Gestion des timeouts

## 🐛 Debugging

### Logs détaillés
```bash
pytest -v --log-cli-level=DEBUG
```

### Breakpoints
```python
import pdb; pdb.set_trace()
# ou
import ipdb; ipdb.set_trace()
```

## 📊 Best Practices

1. **Organisation**
   - Un fichier de test par module
   - Nommage clair et descriptif
   - Documentation des cas complexes

2. **Mocking**
   - Mock uniquement le nécessaire
   - Utiliser les specs pour la validation
   - Reset des mocks entre les tests

3. **Assertions**
   - Vérifications précises
   - Messages d'erreur clairs
   - Validation des effets de bord

4. **Maintenance**
   - Mise à jour avec le code
   - Revue régulière des tests
   - Nettoyage du code mort

## 👷 Contribution

1. **Nouveaux tests**
   - Suivre la structure existante
   - Documenter les cas complexes
   - Vérifier la couverture

2. **Modifications**
   - Maintenir les tests existants
   - Ajouter les nouveaux cas
   - Mettre à jour la documentation

## 🔮 TODO

- [ ] Ajouter des tests de performances
- [ ] Implémenter des tests d'intégration
- [ ] Améliorer la couverture async
- [ ] Ajouter des tests de charge