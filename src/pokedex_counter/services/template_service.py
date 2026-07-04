# vision/templates.py
from pathlib import Path
import cv2

class TemplateService:
    def __init__(self, folder: Path):
        self.templates = {}

        for p in folder.iterdir():
            if p.suffix.lower() in {".png", ".jpg"}:
                img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
                self.templates[p.stem] = img