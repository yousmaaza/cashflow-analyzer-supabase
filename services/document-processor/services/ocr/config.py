from pathlib import Path

class OCRConfig:
    def __init__(self, 
                 x_tolerance: int = 15, 
                 debit_x_tolerance: int = 10, 
                 y_tolerance: int = 10,
                 temp_dir: str = "temp"):
        self.x_tolerance = x_tolerance
        self.debit_x_tolerance = debit_x_tolerance
        self.y_tolerance = y_tolerance
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)

    @property
    def temp_region_path(self) -> Path:
        return self.temp_dir / "temp_region.jpg"