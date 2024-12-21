import argparse
from pathlib import Path
from doctr.models import ocr_predictor
import torch

from services.config import ServiceConfig
from services.ocr.extractor import OcrExtractor
from services.ocr.image_processor import ImageProcessor
from services.ocr.line_processor import LineProcessor
from services.ocr.word_processor import WordProcessor

def main():
    parser = argparse.ArgumentParser(description='Process PDF documents and extract transactions')
    parser.add_argument('pdf_path', type=str, help='Path to the PDF file to process')
    args = parser.parse_args()

    # Vérifier que le fichier existe
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: File {pdf_path} does not exist")
        return

    if not pdf_path.suffix.lower() == '.pdf':
        print("Error: File must be a PDF")
        return

    try:
        # Initialisation des composants
        config = ServiceConfig()
        device = config.tableau.torch_device
        ocr_model = ocr_predictor(pretrained=True).to(device)

        # Création des processeurs
        word_processor = WordProcessor()
        line_processor = LineProcessor()
        image_processor = ImageProcessor()
        
        # Création de l'extracteur OCR
        ocr_extractor = OcrExtractor(
            ocr_model=ocr_model,
            config=config,
            word_processor=word_processor,
            line_processor=line_processor,
            image_processor=image_processor
        )

        # Traitement du document
        results = ocr_extractor.process_document(str(pdf_path))
        
        if results:
            print("\nExtracted text blocks:")
            for idx, block in enumerate(results, 1):
                print(f"\nBlock {idx}:")
                print(block)
        else:
            print("No text blocks were extracted from the document")

    except Exception as e:
        print(f"Error processing document: {str(e)}")

if __name__ == "__main__":
    main()
