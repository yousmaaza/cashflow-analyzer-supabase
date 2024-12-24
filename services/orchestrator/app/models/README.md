# Modèles de données de l'Orchestrateur

Ce module contient les modèles de données (schemas) utilisés par le service d'orchestration pour gérer les workflows de traitement des documents et transactions.

## 📂 Structure

```
models/
├── __init__.py      # Export des modèles
├── schemas.py       # Modèles de base
├── requests.py      # Modèles de requêtes API
├── responses.py     # Modèles de réponses API
└── README.md       # Cette documentation
```

## 🔄 Workflow States

Les états possibles d'un workflow sont :

- `PENDING` : Workflow créé, en attente de traitement
- `DOCUMENT_PROCESSING` : Document en cours de traitement
- `TRANSACTION_ANALYSIS` : Transactions en cours d'analyse
- `STORAGE` : Données en cours de stockage
- `COMPLETED` : Workflow terminé avec succès
- `FAILED` : Workflow échoué

## 📊 Modèles principaux

### WorkflowBase
Modèle de base pour un workflow :
```python
class WorkflowBase:
    user_id: str
    document_path: str
```

### Workflow
Modèle complet d'un workflow :
```python
class Workflow:
    id: str
    state: WorkflowState
    created_at: datetime
    updated_at: datetime
    error: Optional[str]
    results: Dict
    retries: int
```

## 🌐 Modèles API

### Requêtes

- `WorkflowStartRequest` : Démarrage d'un workflow
- `WorkflowRetryRequest` : Nouvelle tentative
- `WorkflowListRequest` : Liste des workflows
- `WorkflowCancelRequest` : Annulation d'un workflow

### Réponses

- `WorkflowResponse` : État d'un workflow
- `WorkflowListResponse` : Liste paginée
- `ErrorResponse` : Format d'erreur standard
- `WorkflowProgressResponse` : Progression
- `ServiceHealthResponse` : État des services

## 🔍 Résultats de traitement

### DocumentProcessingResult
Résultat du traitement d'un document :
```python
class DocumentProcessingResult:
    page_count: int
    processing_time: float
    transactions: List[Dict]
    error: Optional[str]
```

### TransactionAnalysisResult
Résultat de l'analyse des transactions :
```python
class TransactionAnalysisResult:
    processing_time: float
    transactions: List[Dict]
    error: Optional[str]
```

## 💡 Utilisation

### Import des modèles
```python
from app.models import (
    Workflow,
    WorkflowState,
    WorkflowStartRequest,
    WorkflowResponse
)
```

### Exemple de création de workflow
```python
workflow = Workflow(
    id="uuid4()",
    user_id="user123",
    document_path="/path/to/doc.pdf",
    state=WorkflowState.PENDING
)
```

## 🔒 Validation

Tous les modèles sont basés sur Pydantic et incluent :
- Validation des types
- Validation des contraintes
- Conversion automatique des types
- Serialization JSON

## 📝 Maintenance

Pour ajouter un nouveau modèle :
1. Créer la classe dans le fichier approprié
2. Ajouter les imports dans `__init__.py`
3. Mettre à jour cette documentation
4. Ajouter des tests unitaires