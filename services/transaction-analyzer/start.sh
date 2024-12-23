#!/bin/bash

# Démarrage d'Ollama en arrière-plan
ollama serve &

# Attendre que Ollama soit prêt
echo "Waiting for Ollama to start..."
sleep 5

# Téléchargement du modèle Llama3
echo "Pulling Llama3.2 model..."
ollama pull llama3.2

# Démarrage de l'application FastAPI
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000