import os, random, shutil
from pathlib import Path

SRC_DIR = "data_clean_dedup"
OUT_DIR = "data_split"

# ─── CHANGE 1: Add non_seaweed to the class list ─────────────────────────────
CLASSES = ["gracilaria", "kappaphycus", "non_seaweed"]
# ─────────────────────────────────────────────────────────────────────────────

TRAIN = 0.70
VAL   = 0.15
TEST  = 0.15

random.seed(42)

def ensure_dirs():
    for split in ["train", "val", "test"]:
        for cls in CLASSES:
            Path(f"{OUT_DIR}/{split}/{cls}").mkdir(parents=True, exist_ok=True)

ensure_dirs()

for cls in CLASSES:
    src = Path(SRC_DIR) / cls
    files = [p for p in src.iterdir() if p.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]]
    random.shuffle(files)

    n       = len(files)
    n_train = int(n * TRAIN)
    n_val   = int(n * VAL)

    train_files = files[:n_train]
    val_files   = files[n_train:n_train + n_val]
    test_files  = files[n_train + n_val:]

    for p in train_files:
        shutil.copy2(p, f"{OUT_DIR}/train/{cls}/{p.name}")
    for p in val_files:
        shutil.copy2(p, f"{OUT_DIR}/val/{cls}/{p.name}")
    for p in test_files:
        shutil.copy2(p, f"{OUT_DIR}/test/{cls}/{p.name}")

    print(cls, "→ total:", n, "| train:", len(train_files), "| val:", len(val_files), "| test:", len(test_files))