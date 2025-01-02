from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import tempfile
import shutil
from core.logger import log
from services.processor.processor import DocumentProcessor
from core.config import ServiceConfig
from services.ocr.extractor import OcrExtractor
from services.tableau.extractor import TableauExtractor
from doctr.models import ocr_predictor
from time import time


router = APIRouter(
    prefix="/api/v1/pdf_processor",
    tags=["Document"]
)

config = ServiceConfig()

class PDFProcessor:
    def __init__(self):
        log.info("📦 Initializing PDFProcessor...")
        device = config.tableau.torch_device
        self.ocr_model = ocr_predictor(pretrained=True).to(device)
        log.info(f"✅ OCR model loaded successfully on device: {device}")

    def process_pdf(self, pdf_path: Path):
        log.log_process_start(pdf_path.name)
        start_time = time()

        try:
            tableau_extractor = TableauExtractor(config)
            ocr_extractor = OcrExtractor(
                ocr_model=self.ocr_model,
                config=config
            )
            log.debug("🔧 Extractors initialized successfully")

            processor = DocumentProcessor(
                tableau_extractor=tableau_extractor,
                ocr_extractor=ocr_extractor,
                config=config
            )

            results = processor.process_document(pdf_path)
            duration = time() - start_time
            log.log_process_end(pdf_path.name, duration)

            return results

        except Exception as e:
            log.log_error(e, f"processing {pdf_path.name}")
            raise

@router.post("/process/")
async def process_pdf(file: UploadFile = File(...)):
    log.info(f"📝 Received file: {file.filename}")

    if not file.filename.endswith('.pdf'):
        log.warning(f"⚠️ Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        shutil.copyfileobj(file.file, tmp)
        pdf_path = Path(tmp.name)

    try:

        processor = PDFProcessor()
        results = processor.process_pdf(pdf_path)

        if results and results.transactions:
            response_data = {
                "message": "PDF processed successfully",
                "transactions": [t.__dict__ for t in results.transactions],
                "transaction_count": len(results.transactions),
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
        pdf_path.unlink()

