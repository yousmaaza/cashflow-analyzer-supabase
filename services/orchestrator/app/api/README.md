# API Orchestrateur

API REST pour l'orchestration des workflows de traitement de documents bancaires.

## ⚙️ Pré-requis

### 1. Infrastructure
- Python 3.10+
- Docker + Docker Compose
- Compte Supabase actif
- Au moins 2Go de RAM disponible

### 2. Services dépendants
- Document Processor (service de traitement des documents)
- Transaction Analyzer (service d'analyse des transactions)
- Supabase (stockage et authentification)

### 3. Configuration requise
```bash
# Configuration de l'environnement
cp .env.example .env

# Remplir les variables suivantes :
SUPABASE_URL=votre_url_supabase
SUPABASE_KEY=votre_clé_supabase
API_KEY=votre_clé_api_secrète
```

### 4. Initialisation Supabase
```bash
# Exécuter les migrations
cd migrations/
supabase db reset
```

## 💻 Utilisation pas à pas

### 1. Préparation du document
- Format accepté : PDF
- Taille maximale : 10MB
- Document lisible et non protégé

### 2. Création d'un workflow
```bash
# 1. Envoi du document
curl -X POST "http://localhost:8000/api/v1/workflow" \
     -H "X-API-Key: votre_clé_api" \
     -H "X-User-ID: identifiant_utilisateur" \
     -F "document=@chemin/vers/relevé.pdf"

# Réponse attendue
{
    "workflow_id": "abc-123",
    "message": "Workflow started successfully",
    "state": "pending"
}
```

### 3. Suivi du traitement
```bash
# 2. Vérification du statut
curl "http://localhost:8000/api/v1/workflow/abc-123" \
     -H "X-API-Key: votre_clé_api" \
     -H "X-User-ID: identifiant_utilisateur"

# États possibles
{
    "id": "abc-123",
    "state": "document_processing", # En cours de traitement
    "progress": 45.5,
    "message": "Processing document page 2/4"
}
```

### 4. États du workflow
1. `pending` : En attente de traitement
2. `document_processing` : Extraction des données
3. `transaction_analysis` : Catégorisation des transactions
4. `storage` : Stockage des résultats
5. `completed` : Terminé avec succès
6. `failed` : Échec du traitement

### 5. Gestion des erreurs
```bash
# En cas d'échec, vérifier l'erreur
curl "http://localhost:8000/api/v1/workflow/abc-123" \
     -H "X-API-Key: votre_clé_api"

# Réponse en cas d'erreur
{
    "id": "abc-123",
    "state": "failed",
    "error": "Failed to process document: Invalid format"
}

# Retry possible
curl -X POST "http://localhost:8000/api/v1/workflow/abc-123/retry" \
     -H "X-API-Key: votre_clé_api"
```

### 6. Récupération des résultats
```bash
# Liste des workflows
curl "http://localhost:8000/api/v1/workflows?page=1&state=completed" \
     -H "X-API-Key: votre_clé_api" \
     -H "X-User-ID: identifiant_utilisateur"

# Récupération des transactions
# Les transactions sont automatiquement stockées dans Supabase
# Une fois le workflow complété
```

## 📈 Monitoring

### Vérification de l'état des services
```bash
# Health check
curl "http://localhost:8000/api/v1/health"

# Réponse
{
    "healthy": true,
    "services": {
        "document_processor": {
            "status": "healthy",
            "latency": 42.5
        },
        "transaction_analyzer": {
            "status": "healthy",
            "latency": 35.2
        },
        "database": {
            "status": "healthy",
            "connections": 5
        }
    }
}
```

## 🔧 Troubleshooting

### Problèmes courants

1. **Document non traité**
   - Vérifier le format du PDF
   - Confirmer la taille < 10MB
   - Vérifier les logs du Document Processor

2. **Erreur d'analyse**
   - Confirmer la qualité du document
   - Vérifier la connection au Transaction Analyzer
   - Consulter les logs d'erreur

3. **Problèmes de stockage**
   - Vérifier la connection Supabase
   - Confirmer les droits d'accès
   - Vérifier l'espace disponible

### Logs
```bash
# Consulter les logs
tail -f logs/app.log

# Logs d'erreur spécifiques
tail -f logs/error.log
```

## 📃 Limites et quotas

- Taille maximale document : 10MB
- Rate limit API : 100 requêtes/minute
- Timeout traitement : 5 minutes
- Retention logs : 30 jours
- Maximum retry : 3 tentatives

## 💬 Support

1. Vérifier la documentation : /docs
2. Consulter les logs
3. Ouvrir une issue sur GitHub
4. Contacter le support technique