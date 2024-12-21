from typing import List
from .models import Word, Line
from .config import OCRConfig

class LineProcessor:
    def __init__(self, config: OCRConfig):
        self.config = config

    def process_lines(self, words: List[Word]) -> List[Line]:
        """Process words into lines"""
        if not words:
            return []

        sorted_words = sorted(words, key=lambda w: w.y_center)
        lines = []
        current_line = [sorted_words[0]]
        current_y = sorted_words[0].y_center

        for word in sorted_words[1:]:
            if abs(word.y_center - current_y) <= self.config.y_tolerance:
                current_line.append(word)
            else:
                line = self._create_line(current_line)
                lines.append(line)
                current_line = [word]
                current_y = word.y_center

        if current_line:
            line = self._create_line(current_line)
            lines.append(line)

        return sorted(lines, key=lambda x: x.y_position)

    def _create_line(self, words: List[Word]) -> Line:
        """Create a new line from words"""
        words.sort(key=lambda w: w.x_center)
        y_position = sum(w.y_center for w in words) / len(words)
        return Line(words=words, y_position=y_position)