# Utiliser une image de base avec CUDA support si GPU disponible
FROM python:3.10-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installation d'Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Configuration du répertoire de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p data/patterns data/cache logs

# Exposition du port
EXPOSE 8000

# Script de démarrage
COPY start.sh .
RUN chmod +x start.sh

# Commande de démarrage
CMD ["./start.sh"]