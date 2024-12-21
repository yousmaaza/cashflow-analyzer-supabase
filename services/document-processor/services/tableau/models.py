from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

@dataclass
class TableBox:
    x1: int
    y1: int
    x2: int
    y2: int

    @classmethod
    def from_coordinates(cls, coordinates: List[float]):
        return cls(*map(int, coordinates))

    def to_list(self) -> List[float]:
        return [self.x1, self.y1, self.x2, self.y2]

    def extract_region(self, image: np.ndarray) -> np.ndarray:
        return image[self.y1:self.y2, self.x1:self.x2]

@dataclass
class ProcessedTable:
    image: np.ndarray
    coordinates: TableBox
    page_number: int