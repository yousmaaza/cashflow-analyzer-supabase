import os
from pathlib import Path
import tempfile
import shutil
from doctr.models import ocr_predictor
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from time import time

from services.ocr.extractor import OcrExtractor
from services.tableau.extractor import TableauExtractor
from services.processor.processor import DocumentProcessor
from services.config import ServiceConfig
from core.logger import log

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des composants globaux
config = ServiceConfig()

class PDFProcessor:
    def __init__(self):
        # Initialisation du modèle OCR
        log.info("📦 Initializing PDFProcessor...")
        device = config.tableau.torch_device
        self.ocr_model = ocr_predictor(pretrained=True).to(device)
        log.info(f"✅ OCR model loaded successfully on device: {device}")

    def process_pdf(self, pdf_path: Path):
        log.log_process_start(pdf_path.name)
        start_time = time()

        try:
            # Création des extracteurs
            tableau_extractor = TableauExtractor(config)
            ocr_extractor = OcrExtractor(
                ocr_model=self.ocr_model,
                config=config
            )
            log.debug("🔧 Extractors initialized successfully")

            # Création du processor principal
            processor = DocumentProcessor(
                tableau_extractor=tableau_extractor,
                ocr_extractor=ocr_extractor,
                config=config
            )

            # Traitement du document
            results = processor.process_document(pdf_path)
            duration = time() - start_time
            log.log_process_end(pdf_path.name, duration)

            return results

        except Exception as e:
            log.log_error(e, f"processing {pdf_path.name}")
            raise

@app.post("/process/")
async def process_pdf(file: UploadFile = File(...)):
    log.info(f"📝 Received file: {file.filename}")
    
    # Validation du type de fichier
    if not file.filename.endswith('.pdf'):
        log.warning(f"⚠️ Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Création d'un fichier temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = Path(tmp.name)

    try:
        # Traitement du PDF
        processor = PDFProcessor()
        results = processor.process_pdf(pdf_path)

        # Vérification et formatage des résultats
        if results and results.transactions:
            response_data = {
                "message": "PDF processed successfully",
                "transactions": [t.__dict__ for t in results.transactions]
            }
            log.log_result({
                "filename": file.filename,
                "transaction_count": len(results.transactions)
            })
            return response_data

        log.warning(f"⚠️ No transactions found in: {file.filename}")
        raise HTTPException(status_code=400, detail="No transactions found in PDF")

    except Exception as e:
        log.log_error(e, "API endpoint")
        raise HTTPException(status_code=500)
    finally:
        # Nettoyage du fichier temporaire
        pdf_path.unlink()

# Pour lancer directement avec python main.py
if __name__ == "__main__":
    log.info("🚀 Starting Document Processor Service...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)