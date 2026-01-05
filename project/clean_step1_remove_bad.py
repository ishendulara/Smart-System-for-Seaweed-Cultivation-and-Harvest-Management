import os
from PIL import Image
from tqdm import tqdm # pyright: ignore[reportMissingModuleSource]
import shutil

RAW_DIR = "data_raw"
CLEAN_DIR = "data_clean"

CLASSES = ["gracilaria", "kappaphycus"]

os.makedirs(CLEAN_DIR, exist_ok=True)

def is_image_ok(path: str) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()  # verifies file integrity
        with Image.open(path) as img:
            img.convert("RGB")  # ensure readable
        return True
    except Exception:
        return False

for cls in CLASSES:
    src = os.path.join(RAW_DIR, cls)
    dst = os.path.join(CLEAN_DIR, cls)
    os.makedirs(dst, exist_ok=True)

    files = [f for f in os.listdir(src) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    removed = 0

    for f in tqdm(files, desc=f"Checking {cls}"):
        p = os.path.join(src, f)
        if is_image_ok(p):
            shutil.copy2(p, os.path.join(dst, f))
        else:
            removed += 1

    print(f"{cls}: copied {len(files)-removed}, removed {removed}")