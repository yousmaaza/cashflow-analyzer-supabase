from dataclasses import dataclass
from typing import List

@dataclass
class BoundingBox:
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def x_center(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def y_center(self) -> float:
        return (self.y1 + self.y2) / 2

@dataclass
class Word:
    text: str
    confidence: float
    bbox: BoundingBox
    
    @property
    def x_center(self) -> float:
        return self.bbox.x_center

    @property
    def y_center(self) -> float:
        return self.bbox.y_center

    @staticmethod
    def is_number(text: str) -> bool:
        return all(c.isdigit() or c in '., ' for c in text)

    def is_same_type(self, other: 'Word') -> bool:
        return self.is_number(self.text) == self.is_number(other.text)

@dataclass
class Line:
    words: List[Word]
    y_position: float