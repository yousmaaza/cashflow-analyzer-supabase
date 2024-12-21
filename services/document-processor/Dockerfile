FROM python:3.10-slim

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie des fichiers requis
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Création du dossier temporaire
RUN mkdir -p temp

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]