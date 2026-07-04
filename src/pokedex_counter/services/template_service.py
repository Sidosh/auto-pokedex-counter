from pathlib import Path
import cv2

class TemplateService:
    def __init__(self, folder: Path):
        self.templates = {}

        for p in folder.iterdir():
            if p.suffix.lower() not in {".png", ".jpg"}:
                continue

            img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)

            if img is None:
                print(f"[TemplateService] WARNING: failed to load '{p.name}', skipping")
                continue

            self.templates[p.stem] = img