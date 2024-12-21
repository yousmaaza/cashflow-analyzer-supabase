class DocumentProcessor:
    def __init__(self, tableau_extractor, ocr_extractor):
        self.tableau_extractor = tableau_extractor
        self.ocr_extractor = ocr_extractor

    def process_document(self, pdf_path):
        # Convert PDF to image
        images = self.tableau_extractor.convert_pdf_to_image()
        results = []

        for idx, image in enumerate(images):
            # Process page
            page_results = self.process_page(image, idx)
            if page_results:
                results.extend(page_results)

        return {'transactions': results}

    def process_page(self, image, page_num):
        # Detect tables in the image
        table_boxes = self.tableau_extractor.detect_tables(image)
        page_results = []

        for box in table_boxes:
            # Extract text from each detected table
            lines = self.ocr_extractor.extract_text_from_region(image, box)
            
            # Process extracted text
            transactions = self.process_lines(lines)
            if transactions:
                page_results.extend(transactions)

        return page_results

    def process_lines(self, lines):
        transactions = []
        current_date = None

        for line in lines:
            text = ' '.join(word['text'] for word in line['words'])
            
            # Process the line to extract transaction data
            transaction = self.extract_transaction_data(text, current_date)
            if transaction:
                if 'date' in transaction:
                    current_date = transaction['date']
                transactions.append(transaction)

        return transactions

    def extract_transaction_data(self, text, current_date):
        """Extract transaction data from text line.
        This is a simplified version - you'll need to adapt it to your specific bank statement format."""
        # Implementation would depend on your specific bank statement format
        # This is just a placeholder
        return {
            'date': current_date,
            'description': text,
            'amount': 0.0,
            'type': 'unknown'
        }