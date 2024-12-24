# CashFlow Analyzer - Version Supabase

## Description
CashFlow Analyzer est un système de microservices Python conçu pour analyser automatiquement les relevés bancaires PDF. Le projet utilise Supabase comme backend et est structuré en services indépendants pour une meilleure scalabilité et maintenance.

[... reste du contenu précédent ...]

## Utilisation Étape par Étape

### 1. Préparation Initiale

#### 1.1 Préparer votre environnement
```bash
# Cloner le repository
git clone https://github.com/yousmaaza/cashflow-analyzer-supabase.git
cd cashflow-analyzer-supabase

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Sur Windows : .venv\Scripts\activate
```

#### 1.2 Configuration Supabase
1. Créez un nouveau projet sur [Supabase](https://supabase.com/)
2. Récupérez votre URL et clé API
3. Copiez le fichier `.env.example` en `.env`
```bash
cp .env.example .env
```
4. Éditez le fichier `.env` avec vos identifiants Supabase

### 2. Installation des Dépendances et Build

#### 2.1 Installation avec Docker
```bash
# Construire les images Docker
docker-compose build

# Vérifier les images construites
docker images
```

#### 2.2 Installation manuelle (optionnel)
```bash
# Installer les dépendances Python
pip install -r requirements.txt
```

### 3. Démarrage des Services

#### 3.1 Démarrage avec Docker
```bash
# Lancer tous les services
docker-compose up -d

# Vérifier les services en cours
docker-compose ps
```

#### 3.2 Vérification des Services
- Document Processor : http://localhost:8081
- Transaction Analyzer : http://localhost:8082
- Data Manager : http://localhost:8083

### 4. Processus de Traitement des Documents

#### 4.1 Préparer un Relevé Bancaire
- Assurez-vous d'avoir un relevé bancaire au format PDF
- Le PDF doit contenir des transactions lisibles

#### 4.2 Traitement du Document
1. Utilisez l'endpoint `/process` du Document Processor
2. Envoyez votre fichier PDF via une requête POST
3. Le service va :
   - Convertir le PDF en images
   - Détecter les tableaux
   - Extraire les transactions
   - Retourner un JSON structuré

### 5. Analyse des Transactions

#### 5.1 Catégorisation Automatique
- Utilisez l'endpoint `/analyze` du Transaction Analyzer
- Envoyez les transactions extraites
- L'IA va catégoriser automatiquement chaque transaction

#### 5.2 Visualisation des Données
- Consultez le Data Manager pour voir les transactions stockées
- Filtrez, triez et analysez vos transactions

### 6. Personnalisation et Paramétrage

#### 6.1 Configuration Avancée
- Modifiez `config.yaml` dans chaque service pour ajuster :
  - Seuils de détection
  - Configurations LLM
  - Paramètres de traitement

#### 6.2 Ajout de Nouvelles Fonctionnalités
- Étendez les services existants
- Ajoutez de nouveaux modèles d'IA
- Personnalisez les analyses

### 7. Surveillance et Logs

#### 7.1 Suivi des Logs
```bash
# Logs d'un service spécifique
docker-compose logs document-processor
docker-compose logs transaction-analyzer
```

#### 7.2 Débogage
- Vérifiez les logs pour les erreurs
- Utilisez les endpoints de healthcheck
- Consultez la documentation de chaque service

### 8. Mise à Jour et Maintenance

#### 8.1 Mises à Jour
```bash
# Mettre à jour les images
docker-compose pull

# Reconstruire et redémarrer
docker-compose up -d --build
```

#### 8.2 Sauvegarde des Données
- Utilisez les fonctionnalités de backup de Supabase
- Exportez régulièrement vos données

## Conseils Supplémentaires

- Utilisez un PDF de test pour valider l'installation
- Commencez avec un petit nombre de transactions
- Ajustez progressivement les configurations

Bon voyage dans l'analyse de vos finances ! 🚀📊