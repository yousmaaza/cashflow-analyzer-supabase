# Document Processor Service

Service de traitement des documents PDF pour l'extraction des transactions bancaires. Ce service utilise l'OCR (Optical Character Recognition) et la détection de tableaux pour extraire automatiquement les informations des relevés bancaires.

## Fonctionnalités

- Conversion PDF vers image
- Détection automatique des tableaux avec YOLO
- OCR avec doctr
- Extraction structurée des transactions
- API REST avec FastAPI

## Prérequis

- Python 3.10+
- Docker et Docker Compose
- Compte Supabase
- 2Go de RAM minimum
- GPU recommandé pour de meilleures performances

## Structure du Service

```
document-processor/
├── services/
│   ├── document_processor.py    # Logique principale
│   ├── ocr_extractor.py         # Extraction OCR
│   └── tableau_extractor.py     # Détection des tableaux
├── config.py                    # Configuration
├── main.py                      # Point d'entrée FastAPI
├── requirements.txt             # Dépendances Python
└── Dockerfile                   # Configuration Docker
```

## Configuration

### Variables d'Environnement

Créez un fichier `.env` avec :

```env
SUPABASE_URL=votre_url_supabase
SUPABASE_KEY=votre_clé_supabase
SUPABASE_JWT_SECRET=votre_secret_jwt
MAX_FILE_SIZE_MB=10
```

## Installation

### Développement Local

1. Créer l'environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Démarrer le service :
```bash
uvicorn main:app --reload --port 8080
```

### Avec Docker

1. Construire l'image :
```bash
docker build -t document-processor .
```

2. Lancer le conteneur :
```bash
docker run -p 8080:8080 \
  -e SUPABASE_URL=votre_url \
  -e SUPABASE_KEY=votre_clé \
  -e SUPABASE_JWT_SECRET=votre_secret \
  document-processor
```

### Avec Docker Compose

```bash
docker-compose up document-processor
```

## Utilisation de l'API

### Traiter un PDF

```bash
curl -X POST "http://localhost:8080/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@relevé_bancaire.pdf"
```

Réponse :
```json
{
  "message": "PDF processed successfully",
  "transactions": [
    {
      "date": "2024-01-15",
      "description": "PAIEMENT CB CARREFOUR",
      "amount": -42.50,
      "type": "DEBIT"
    }
  ]
}
```

## Déploiement

### Sur un serveur

1. Cloner le repository
```bash
git clone <repo_url>
cd document-processor
```

2. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

3. Déployer avec Docker Compose
```bash
docker-compose up -d
```

### Sur Supabase Edge Functions

1. Installer Supabase CLI
```bash
npm install -g supabase
```

2. Se connecter à votre projet
```bash
supabase login
```

3. Déployer la fonction
```bash
supabase functions deploy document-processor
```

## Monitoring

- Logs Docker : `docker logs document-processor`
- Metrics FastAPI : `http://localhost:8080/metrics`
- Documentation API : `http://localhost:8080/docs`

## Dépannage

### Problèmes Courants

1. **Erreur OCR**
   - Vérifier la qualité du PDF
   - Augmenter la RAM allouée à Docker

2. **Timeout lors du traitement**
   - Augmenter la limite de timeout dans la config
   - Réduire la taille du PDF

3. **Erreur GPU**
   - Vérifier l'installation des drivers CUDA
   - Basculer en mode CPU dans config.py

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amélioration`)
3. Commit (`git commit -m 'Ajoute une fonctionnalité'`)
4. Push (`git push origin feature/amélioration`)
5. Créer une Pull Request

## Support

- Ouvrir une issue sur GitHub
- Consulter la documentation Supabase
- Vérifier les logs Docker