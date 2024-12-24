# API Orchestrateur

Ce module contient l'implémentation de l'API REST pour le service d'orchestration des workflows de traitement de documents bancaires.

## 📚 Structure

```
api/
├── __init__.py
├── routes.py       # Définition des endpoints
├── dependencies.py  # Dépendances FastAPI
└── README.md      # Cette documentation
```

## 🏷️ Endpoints

### Gestion des Workflows

#### `POST /api/v1/workflow`
Crée un nouveau workflow de traitement.
- Accept: multipart/form-data
- Body:
  - document (file): Document bancaire (PDF)
  - user_id (string): Identifiant utilisateur

#### `GET /api/v1/workflow/{workflow_id}`
Récupère le statut d'un workflow.
- Paramètres:
  - workflow_id: Identifiant du workflow

#### `GET /api/v1/workflows`
Liste les workflows d'un utilisateur.
- Query params:
  - page (int, default=1)
  - page_size (int, default=10)
  - state (string, optional)

#### `POST /api/v1/workflow/{workflow_id}/retry`
Retente un workflow échoué.

### Surveillance

#### `GET /api/v1/health`
Vérifie l'état du service.

## 🔐 Sécurité

### Authentication
```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != config.api.api_key:
        raise HTTPException(status_code=403)
```

### Headers Requis
- X-API-Key: Clé d'API
- X-User-ID: Identifiant utilisateur

## 🛠 Dépendances

### Services
```python
def get_workflow_service():
    config = ServiceConfig()
    return WorkflowService(config)
```

### Validation
```python
async def validate_workflow_access(
    workflow_id: str,
    user_id: str
) -> bool:
    # Vérifie les droits d'accès
```

## ⚠️ Gestion des Erreurs

### Codes HTTP
- 200: Succès
- 400: Erreur de requête
- 401: Non authentifié
- 403: Non autorisé
- 404: Ressource non trouvée
- 500: Erreur serveur

### Format d'Erreur
```json
{
    "error": "Message d'erreur",
    "detail": "Détails techniques",
    "workflow_id": "ID optionnel"
}
```

## 💡 Exemples d'Utilisation

### Créer un Workflow
```bash
curl -X POST "http://localhost:8000/api/v1/workflow" \
     -H "X-API-Key: your-key" \
     -H "X-User-ID: user123" \
     -F "document=@releve.pdf"
```

### Vérifier le Statut
```bash
curl "http://localhost:8000/api/v1/workflow/abc-123" \
     -H "X-API-Key: your-key" \
     -H "X-User-ID: user123"
```

## 📊 Monitoring

### Métriques
- Latence des requêtes
- Taux de succès/échec
- Nombre de workflows actifs

### Logs
Chaque endpoint génère des logs structurés:
```python
log.info("Creating workflow", extra={
    "user_id": user_id,
    "document": document.filename
})
```

## 🧪 Tests

Les tests pour l'API se trouvent dans `tests/api/`

### Exécution
```bash
pytest tests/api/
pytest tests/api/test_routes.py -k "test_create_workflow"
```

### Exemple de Test
```python
async def test_create_workflow(client):
    response = await client.post(
        "/api/v1/workflow",
        files={'document': open('test.pdf', 'rb')},
        headers={'X-User-ID': 'test-user'}
    )
    assert response.status_code == 200
```

## 👷 Contribution

1. Vérifier la couverture de tests
2. Suivre les conventions FastAPI
3. Documenter les nouveaux endpoints
4. Utiliser les types Pydantic

## 📙 Documentation

La documentation OpenAPI est disponible sur:
- /docs : Documentation Swagger
- /redoc : Documentation ReDoc