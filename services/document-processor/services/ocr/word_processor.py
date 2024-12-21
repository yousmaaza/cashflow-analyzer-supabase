from typing import List, Optional
from .models import Word, BoundingBox
from .config import OCRConfig

class WordProcessor:
    def __init__(self, config: OCRConfig):
        self.config = config

    def find_debit_column(self, words: List[Word]) -> Optional[float]:
        """Find the x-coordinate of the debit column"""
        for word in words:
            if word.text.upper() == "DEBIT":
                return word.bbox.x_center
        return None

    def process_debit_amounts(self, words: List[Word], debit_x: Optional[float]) -> List[Word]:
        """Process and mark debit amounts"""
        if not debit_x:
            return words

        processed_words = []
        for word in words:
            if abs(word.bbox.x_center - debit_x) < self.config.debit_x_tolerance:
                try:
                    number = float(word.text.replace(',', '.').replace(' ', ''))
                    word.text = f"-{abs(number)}"
                except ValueError:
                    pass
            processed_words.append(word)
        return processed_words

    def merge_words(self, words: List[Word]) -> List[Word]:
        """Merge words that are close together"""
        if not words:
            return []

        sorted_words = sorted(words, key=lambda w: w.x_center)
        merged_words = []
        current_group = [sorted_words[0]]

        for word in sorted_words[1:]:
            last_word = current_group[-1]
            distance = word.bbox.x1 - last_word.bbox.x2

            if distance <= self.config.x_tolerance and word.is_same_type(last_word):
                current_group.append(word)
            else:
                merged_word = self._merge_word_group(current_group)
                if merged_word:
                    merged_words.append(merged_word)
                current_group = [word]

        if current_group:
            merged_word = self._merge_word_group(current_group)
            if merged_word:
                merged_words.append(merged_word)

        return merged_words

    def _merge_word_group(self, word_group: List[Word]) -> Optional[Word]:
        """Merge a group of words into a single word"""
        if not word_group:
            return None

        merged_text = ' '.join(word.text for word in word_group)
        avg_confidence = sum(w.confidence for w in word_group) / len(word_group)

        merged_bbox = BoundingBox(
            x1=min(w.bbox.x1 for w in word_group),
            y1=min(w.bbox.y1 for w in word_group),
            x2=max(w.bbox.x2 for w in word_group),
            y2=max(w.bbox.y2 for w in word_group)
        )

        return Word(
            text=merged_text.replace(' ', ''),
            confidence=avg_confidence,
            bbox=merged_bbox
        )