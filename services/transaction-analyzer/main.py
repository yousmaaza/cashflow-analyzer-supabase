import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as transaction_router
from app.core.config import ServiceConfig
from app.core.logger import log

# Création de l'application FastAPI
app = FastAPI(
    title="Transaction Analyzer Service",
    description="Service d'analyse et de catégorisation des transactions bancaires utilisant Llama 3",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # A configurer selon l'environnement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement de la configuration
config = ServiceConfig()

# Ajout des routes
app.include_router(transaction_router)

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'application"""
    log.info("🚀 Starting Transaction Analyzer Service...")
    # Création des dossiers nécessaires
    config.create_directories()
    log.info("✅ Service initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Événement d'arrêt de l'application"""
    log.info("👋 Shutting down Transaction Analyzer Service...")

@app.get("/", tags=["health"])
async def root():
    """Endpoint racine pour vérifier l'état du service"""
    return {
        "service": "Transaction Analyzer",
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Activer le rechargement automatique en développement
    )