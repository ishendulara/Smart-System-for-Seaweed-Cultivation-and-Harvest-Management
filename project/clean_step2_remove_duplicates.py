import os, shutil
from PIL import Image
import imagehash # pyright: ignore[reportMissingImports]
from tqdm import tqdm # pyright: ignore[reportMissingModuleSource]

CLEAN_DIR = "data_clean"
DEDUP_DIR = "data_clean_dedup"
CLASSES = ["gracilaria", "kappaphycus"]

os.makedirs(DEDUP_DIR, exist_ok=True)

# smaller number = stricter. Try 4 or 5 first.
HAMMING_THRESHOLD = 5

def phash(path):
    with Image.open(path) as img:
        img = img.convert("RGB")
        return imagehash.phash(img)

for cls in CLASSES:
    src = os.path.join(CLEAN_DIR, cls)
    dst = os.path.join(DEDUP_DIR, cls)
    os.makedirs(dst, exist_ok=True)

    files = [f for f in os.listdir(src) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]

    hashes = []
    kept = 0
    removed = 0

    for f in tqdm(files, desc=f"De-dup {cls}"):
        p = os.path.join(src, f)
        h = phash(p)

        duplicate = False
        for old_h in hashes:
            if abs(h - old_h) <= HAMMING_THRESHOLD:
                duplicate = True
                break

        if duplicate:
            removed += 1
        else:
            hashes.append(h)
            shutil.copy2(p, os.path.join(dst, f))
            kept += 1

    print(f"{cls}: kept {kept}, removed duplicates {removed}")