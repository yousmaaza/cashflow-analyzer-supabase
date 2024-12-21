# Document Processor Service

Ce service est responsable du traitement des relevés bancaires PDF. Il utilise l'OCR et la détection de tableaux pour extraire automatiquement les transactions.

## Fonctionnalités

- Conversion PDF vers image
- Détection automatique des tableaux avec YOLO
- Extraction de texte avec OCR (doctr)
- API REST pour le traitement des documents
- Gestion des fichiers temporaires
- Support GPU (MPS/CUDA) si disponible

## Prérequis

- Python 3.10+
- Poppler (pour pdf2image)
- OpenCV
- GPU (optionnel)

### Installation des dépendances système

#### Ubuntu/Debian
```bash
apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils
```

#### macOS
```bash
brew install poppler
```

#### Windows
```bash
# Installer poppler via conda
conda install -c conda-forge poppler
```

## Configuration

1. Créez un fichier `.env` :
```bash
cp .env.example .env
```

2. Configurez les variables d'environnement :
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SUPABASE_JWT_SECRET=your_jwt_secret
MAX_FILE_SIZE_MB=10
```

## Installation locale

1. Créez un environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez le service :
```bash
uvicorn main:app --reload --port 8081
```

## Déploiement avec Docker

1. Construction de l'image :
```bash
docker build -t document-processor:latest .
```

2. Lancement du conteneur :
```bash
docker run -d \
    -p 8081:8080 \
    --env-file .env \
    --name document-processor \
    document-processor:latest
```

## Utilisation de l'API

### Traiter un PDF

```bash
curl -X POST http://localhost:8081/process/ \
    -H "Content-Type: multipart/form-data" \
    -F "file=@relevé_bancaire.pdf"
```

Exemple de réponse :
```json
{
    "message": "PDF processed successfully",
    "transactions": [
        {
            "date": "2024-01-15",
            "description": "PAYMENT XYZ",
            "amount": 42.50,
            "type": "DEBIT"
        }
    ]
}
```

## Structure du Code

```
document-processor/
├── services/
│   ├── document_processor.py    # Logique principale
│   ├── ocr_extractor.py        # Extraction OCR
│   └── tableau_extractor.py    # Détection des tableaux
├── main.py                     # Point d'entrée FastAPI
├── config.py                   # Configuration
├── requirements.txt            # Dépendances
└── Dockerfile                  # Configuration Docker
```

## Développement

### Tests Locaux
```bash
pytest tests/
```

### Logs Docker
```bash
docker logs -f document-processor
```

### Rebuild et Redéploiement
```bash
docker-compose up -d --build document-processor
```

## Monitoring

Le service expose les métriques sur `/metrics` pour Prometheus.

Points de surveillance importants :
- Utilisation CPU/GPU
- Temps de traitement PDF
- Taux de réussite OCR
- Erreurs d'extraction

## Dépannage

### Problèmes courants

1. Erreur PDF non lisible :
   - Vérifier les droits d'accès
   - Vérifier la version de Poppler

2. OCR peu précis :
   - Vérifier la qualité du PDF
   - Ajuster les paramètres de tolérance

3. Erreurs mémoire :
   - Ajuster MAX_FILE_SIZE_MB
   - Vérifier la mémoire disponible

## Support

Pour obtenir de l'aide :
1. Consultez les logs : `docker logs document-processor`
2. Vérifiez la documentation API : `/docs`
3. Ouvrez une issue sur GitHub

## Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -m 'Ajout amelioration'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request