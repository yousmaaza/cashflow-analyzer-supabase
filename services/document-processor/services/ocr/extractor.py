import os
import cv2
import numpy as np
from typing import List, Dict, Optional
from doctr.io import DocumentFile

from core.config import ServiceConfig
from core.logger import log
from .models import Word, Line, BoundingBox


class OcrExtractor:
    def __init__(self, ocr_model, config: Optional[ServiceConfig] = None):
        """Initialize OCR Extractor

        Args:
            ocr_model: Pretrained OCR model from doctr
            config: Configuration object for OCR parameters
        """
        self.ocr_model = ocr_model
        self.config = config or ServiceConfig()

        # Ensure temporary directory exists
        self.config.create_directories()

    def extract_text_from_region(self, image: np.ndarray, box: List[float], page_num:int) -> List[Dict]:
        """Extract and process text from image region

        Args:
            image: Input image
            box: Region coordinates [x1, y1, x2, y2]
            page_num: Page number

        Returns:
            List of processed lines with word information
        """
        # Prepare image
        x1, y1, x2, y2 = map(int, box)
        region = image[y1:y2, x1:x2]

        if region.size == 0:
            log.error(f"Empty region extracted for page {page_num} with box {box}")
            return []

        # Save temporary image
        page_image_path = f"{self.config.output_folders.pages}/ocr_page_{page_num}.png"
        cv2.imwrite(page_image_path, cv2.cvtColor(region, cv2.COLOR_BGR2RGB))

        # Extract words from the region
        doc = DocumentFile.from_images(page_image_path)
        result = self.ocr_model(doc)

        # Find debit column (optional)
        debit_x = self._find_debit_column(result, box)

        # Extract and process words
        words = self._extract_words(result, box, debit_x)

        # Group words into lines
        lines = self._group_words_by_line(words)

        # Process lines by merging close words
        processed_lines = []
        for line in lines:
            merged_words = self._merge_close_words(line.words)
            if merged_words:
                processed_lines.append({
                    'words': [self._word_to_dict(word) for word in merged_words],
                    'y_position': line.y_position
                })

        processed_lines.sort(key=lambda x: x['y_position'])

        # Save lines to text file
        text_file_path = f"{self.config.output_folders.text}/page_{page_num}_lines.txt"
        with open(text_file_path, 'w') as f:
            for line in processed_lines:
                f.write(' '.join(word['text'] for word in line['words']) + '\n')


        return processed_lines

    def _find_debit_column(self, doc_result, box: List[float]) -> Optional[float]:
        """Find the x-coordinate of the debit column"""
        x1, y1, x2, y2 = map(int, box)

        for page in doc_result.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        if word.value.upper() == "DEBIT":
                            abs_geom = word.geometry
                            return abs_geom[0][0] * (x2 - x1)
        return None

    def _extract_words(self, doc_result, box: List[float], debit_x: Optional[float]) -> List[Word]:
        """Extract words from OCR result"""
        x1, y1, x2, y2 = map(int, box)
        words = []

        for page in doc_result.pages:
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        # Create relative bounding box
                        bbox = BoundingBox(
                            x1=x1 + int(word.geometry[0][0] * (x2 - x1)),
                            y1=y1 + int(word.geometry[0][1] * (y2 - y1)),
                            x2=x1 + int(word.geometry[1][0] * (x2 - x1)),
                            y2=y1 + int(word.geometry[1][1] * (y2 - y1))
                        )

                        # Process debit amounts if applicable
                        word_text = word.value
                        if debit_x is not None:
                            word_x = word.geometry[0][0] * (x2 - x1)
                            if abs(word_x - debit_x) < self.config.ocr.debit_x_tolerance:
                                try:
                                    number = float(word_text.replace(',', '.').replace(' ', ''))
                                    word_text = f"-{abs(number)}"
                                except ValueError:
                                    pass

                        words.append(Word(
                            text=word_text,
                            confidence=word.confidence,
                            bbox=bbox
                        ))

        return words

    def _group_words_by_line(self, words: List[Word]) -> List[Line]:
        """Group words into lines based on y-coordinate"""
        if not words:
            return []

        # Sort words by y-coordinate
        sorted_words = sorted(words, key=lambda w: w.y_center)
        lines = []
        current_line = [sorted_words[0]]
        current_y = sorted_words[0].y_center

        for word in sorted_words[1:]:
            if abs(word.y_center - current_y) <= self.config.ocr.y_tolerance:
                current_line.append(word)
            else:
                # Sort the current line by x-coordinate
                current_line.sort(key=lambda w: w.x_center)
                lines.append(Line(
                    words=current_line,
                    y_position=sum(w.y_center for w in current_line) / len(current_line)
                ))
                current_line = [word]
                current_y = word.y_center

        # Add the last line
        if current_line:
            current_line.sort(key=lambda w: w.x_center)
            lines.append(Line(
                words=current_line,
                y_position=sum(w.y_center for w in current_line) / len(current_line)
            ))

        return lines

    def _merge_close_words(self, words: List[Word]) -> List[Word]:
        """Merge words that are close together"""
        if not words:
            return []

        sorted_words = sorted(words, key=lambda w: w.x_center)
        merged_words = []
        current_group = [sorted_words[0]]

        for word in sorted_words[1:]:
            last_word = current_group[-1]
            distance = word.bbox.x1 - last_word.bbox.x2

            if (distance <= self.config.ocr.x_tolerance and
                    self._is_same_type(last_word.text, word.text)):
                current_group.append(word)
            else:
                merged_word = self._merge_word_group(current_group)
                if merged_word:
                    merged_words.append(merged_word)
                current_group = [word]

        # Add the last group
        if current_group:
            merged_word = self._merge_word_group(current_group)
            if merged_word:
                merged_words.append(merged_word)

        return merged_words

    def _merge_word_group(self, word_group: List[Word]) -> Optional[Word]:
        """Merge a group of words into a single word"""
        if not word_group:
            return None

        # Merge text
        merged_text = ' '.join(word.text for word in word_group)

        # Create merged bounding box
        merged_bbox = BoundingBox(
            x1=min(w.bbox.x1 for w in word_group),
            y1=min(w.bbox.y1 for w in word_group),
            x2=max(w.bbox.x2 for w in word_group),
            y2=max(w.bbox.y2 for w in word_group)
        )

        # Merge confidence
        avg_confidence = sum(w.confidence for w in word_group) / len(word_group)

        return Word(
            text=merged_text.replace(' ', ''),
            confidence=avg_confidence,
            bbox=merged_bbox
        )

    def _is_same_type(self, text1: str, text2: str) -> bool:
        """Check if two words are of the same type (number or text)"""

        def is_number(text: str) -> bool:
            return all(c.isdigit() or c in '., ' for c in text)

        return is_number(text1) == is_number(text2)

    def _word_to_dict(self, word: Word) -> Dict:
        """Convert Word object to dictionary for compatibility"""
        return {
            'text': word.text,
            'confidence': word.confidence,
            'bbox': vars(word.bbox),
            'y_center': word.y_center,
            'x_center': word.x_center
        }

    def visualize_lines(self, image: np.ndarray, lines: List[Dict]):
        """Visualise the detected lines"""
        img_copy = image.copy()
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]

        for i, line in enumerate(lines):
            color = colors[i % len(colors)]
            y = int(line['y_position'])

            if line['words']:
                x_start = min(w['bbox']['x1'] for w in line['words'])
                x_end = max(w['bbox']['x2'] for w in line['words'])
                cv2.line(img_copy, (x_start - 10, y), (x_end + 10, y), color, 2)

                for word in line['words']:
                    bbox = word['bbox']
                    cv2.rectangle(img_copy, (bbox['x1'], bbox['y1']), (bbox['x2'], bbox['y2']), color, 2)
                    cv2.putText(
                        img_copy,
                        word['text'],
                        (bbox['x1'], bbox['y1'] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2
                    )

        return img_copy