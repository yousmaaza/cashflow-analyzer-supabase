import os
from pathlib import Path
import tempfile
import shutil
from doctr.models import ocr_predictor
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from services.ocr.extractor import OcrExtractor
from services.tableau.extractor import TableauExtractor
from services.processor.processor import DocumentProcessor
from services.config import ServiceConfig

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
        device = config.tableau.torch_device
        self.ocr_model = ocr_predictor(pretrained=True).to(device)

    def process_pdf(self, pdf_path: Path):
        tableau_extractor = TableauExtractor(
            config=config,
            pdf_path=pdf_path
        )
        
        ocr_extractor = OcrExtractor(
            ocr_model=self.ocr_model,
            config=config
        )

        processor = DocumentProcessor(
            tableau_extractor=tableau_extractor,
            ocr_extractor=ocr_extractor,
            config=config
        )

        results = processor.process_document(pdf_path)
        return results

@app.post("/process/")
async def process_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = Path(tmp.name)

    try:
        processor = PDFProcessor()
        results = processor.process_pdf(pdf_path)

        if results and results.transactions:
            return {
                "message": "PDF processed successfully",
                "transactions": [t.dict() for t in results.transactions]
            }

        raise HTTPException(status_code=400, detail="No transactions found in PDF")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        pdf_path.unlink()  # Supprimer le fichier temporaire

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)