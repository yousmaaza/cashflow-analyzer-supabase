# Cashflow Analyzer - Service Orchestrateur

Service d'orchestration pour la gestion des workflows de traitement et d'analyse des transactions bancaires. Ce service coordonne les interactions entre les différents composants du système Cashflow Analyzer.

## 🎯 Fonctionnalités

- Orchestration du flux de traitement des documents bancaires 
- Suivi de l'état des workflows de traitement
- Coordination entre les services :
  - Document Processor : Extraction des données des relevés bancaires
  - Transaction Analyzer : Catégorisation des transactions
  - Supabase : Stockage persistant des données

## 🔄 Workflow

1. Réception d'un document bancaire
2. Création et suivi d'un workflow de traitement
3. Coordination du traitement document → analyse → stockage
4. Notification de l'état d'avancement
5. Gestion des erreurs et reprises

## 🛠 Prérequis

- Python 3.10+
- [Document Processor Service](../document-processor)
- [Transaction Analyzer Service](../transaction-analyzer)
- Compte Supabase

## 🚀 Installation

1. Créer l'environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

4. Démarrer le service :
```bash
uvicorn main:app --reload
```

## 📦 Structure

```
orchestrator/
├── app/
│   ├── api/          # Routes FastAPI
│   ├── core/         # Configuration
│   ├── models/       # Modèles de données
│   └── services/     # Logique métier
├── migrations/       # Scripts SQL Supabase
└── tests/           # Tests unitaires
```

## 🔧 Configuration

### Variables d'Environnement

```env
# Service Configuration
PORT=8000
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Services URLs
DOCUMENT_PROCESSOR_URL=http://localhost:8001
TRANSACTION_ANALYZER_URL=http://localhost:8002
```

## 📊 Endpoints API

### POST /workflow/start
Démarre un nouveau workflow de traitement.
```bash
curl -X POST "http://localhost:8000/workflow/start" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "123", "document_path": "path/to/document.pdf"}'
```

### GET /workflow/{workflow_id}
Récupère l'état d'un workflow.
```bash
curl "http://localhost:8000/workflow/abc-123"
```

## 🧪 Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=app tests/
```

## 🐳 Docker

1. Construction de l'image :
```bash
docker build -t cashflow-orchestrator .
```

2. Lancement :
```bash
docker-compose up
```

## 📝 Tables Supabase

### workflows
Table de suivi des workflows de traitement :
```sql
create table workflows (
  id uuid primary key,
  user_id text not null,
  document_path text not null,
  state text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now()),
  error text,
  results jsonb default '{}'::jsonb
);
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit (`git commit -m 'Ajoute une fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 License

MIT License

## 🆘 Support

- Ouvrir une issue sur GitHub
- Consulter la documentation du projet principal