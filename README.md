# CashFlow Analyzer - Version Supabase

## Description
CashFlow Analyzer est un système de microservices Python conçu pour analyser automatiquement les relevés bancaires PDF. Le projet utilise Supabase comme backend et est structuré en services indépendants pour une meilleure scalabilité et maintenance.

## Architecture

### Structure du Projet
```
cashflow-analyzer-supabase/
├── services/
│   ├── document-processor/     # Service de traitement des documents
│   ├── transaction-analyzer/   # Service d'analyse des transactions
│   └── data-manager/          # Service de gestion des données
├── supabase/
│   └── migrations/            # Scripts SQL pour Supabase
└── tests/                     # Tests unitaires et d'intégration
```

### Services

#### 1. Document Processor
- Conversion des PDFs en images
- Détection des tableaux (YOLO)
- OCR et extraction de texte (doctr)
- Structuration des données extraites

#### 2. Transaction Analyzer
- Analyse des transactions
- Catégorisation automatique
- Détection des patterns
- Génération des statistiques

#### 3. Data Manager
- Interface avec Supabase
- CRUD des transactions
- Gestion du cache
- API pour les données

## Technologies Utilisées

- **Backend**:
  - Python 3.10+
  - Supabase (PostgreSQL)
  - Docker pour le déploiement

- **OCR et Traitement d'Images**:
  - doctr
  - YOLOv8
  - pdf2image
  - OpenCV

- **Analyse de Données**:
  - pandas
  - numpy

## Configuration

### Prérequis
- Python 3.10+
- Docker et Docker Compose
- Compte Supabase

### Variables d'Environnement
Créez un fichier `.env` à partir du `.env.example` :
```bash
cp .env.example .env
```

Variables requises :
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_JWT_SECRET=your_jwt_secret
```

### Configuration Supabase

1. Créez un nouveau projet sur Supabase

2. Exécutez les migrations :
```bash
cd supabase/migrations
# Utilisez l'interface Supabase pour exécuter les scripts SQL
```

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/yousmaaza/cashflow-analyzer-supabase.git
cd cashflow-analyzer-supabase
```

2. Construisez les images Docker :
```bash
docker-compose build
```

## Démarrage

Lancez les services avec Docker Compose :
```bash
docker-compose up -d
```

Services disponibles :
- Document Processor : http://localhost:8081
- Transaction Analyzer : http://localhost:8082
- Data Manager : http://localhost:8083

## Développement

### Installation de l'environnement de développement
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Tests
```bash
pytest tests/
```

### Nouveaux Services
Pour ajouter un nouveau service :
1. Créez un nouveau dossier dans `services/`
2. Ajoutez le Dockerfile et requirements.txt
3. Mettez à jour docker-compose.yml
4. Ajoutez les tests dans `tests/`

## API Reference

### Document Processor
- `POST /process` : Traite un fichier PDF
  - Body: form-data avec fichier PDF
  - Returns: JSON avec les transactions extraites

### Transaction Analyzer
- `POST /analyze` : Analyse des transactions
  - Body: JSON avec liste de transactions
  - Returns: JSON avec analyses et catégories

### Data Manager
- `GET /transactions` : Liste toutes les transactions
- `POST /transactions` : Crée une nouvelle transaction
- `PUT /transactions/{id}` : Met à jour une transaction
- `DELETE /transactions/{id}` : Supprime une transaction

## Sécurité
- Authentification via Supabase
- Row Level Security (RLS) pour les données
- Validation des entrées
- Rate limiting

## Contribution
1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## License
MIT

## Support
Pour toute question ou problème :
1. Ouvrez une issue sur GitHub
2. Contactez les mainteneurs