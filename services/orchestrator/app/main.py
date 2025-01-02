# app/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import ServiceConfig
from app.core.logger import log

app = FastAPI(
   title="Workflow Orchestrator",
   description="Service d'orchestration des workflows de traitement de documents bancaires",
   version="1.0.0"
)

app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"]
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
   log.info("🚀 Starting Workflow Orchestrator Service...")
   config = ServiceConfig()
   config.create_directories()
   log.info("✅ Service initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
   log.info("👋 Shutting down Workflow Orchestrator Service...")

if __name__ == "__main__":
   uvicorn.run("app.main:app", host="0.0.0.0", port=8085, reload=True)