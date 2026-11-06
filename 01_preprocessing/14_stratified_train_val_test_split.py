"""
Rice Leaf Dataset - Train/Validation/Test Split (80/10/10)
===========================================================
Pure Python stratified split.
No scikit-learn required.

Each class is independently split into:
    80% Train
    10% Validation
    10% Test
"""

import os
import shutil
import random

# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_DIR = "./rice_leaf_disease_dataset"
OUTPUT_DIR = "./dataset_audit"

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

SEED = 42

# Reproducibility
random.seed(SEED)

# Supported image formats
EXTENSIONS = (".jpg", ".jpeg", ".png", ".jfif", ".webp")


# ============================================================
# CHECK RATIOS
# ============================================================

assert abs(TRAIN_RATIO + VAL_RATIO + TEST_RATIO - 1.0) < 1e-9, \
    "Train/Validation/Test ratios must add up to 1.0"


# ============================================================
# CLEAN OUTPUT FOLDER (if exists)
# ============================================================

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
    print(f"Removed existing folder: {OUTPUT_DIR}")


# ============================================================
# CREATE OUTPUT FOLDERS
# ============================================================

classes = sorted([
    cls for cls in os.listdir(SOURCE_DIR)
    if os.path.isdir(os.path.join(SOURCE_DIR, cls))
])

for split in ["train", "validation", "test"]:
    for cls in classes:
        os.makedirs(
            os.path.join(OUTPUT_DIR, split, cls),
            exist_ok=True
        )


# ============================================================
# STRATIFIED SPLIT
# ============================================================

print("=" * 70)
print("RICE LEAF DATASET — 80/10/10 STRATIFIED SPLIT")
print("=" * 70)

total_images = 0

split_data = {
    "train": {},
    "validation": {},
    "test": {}
}

# ------------------------------------------------------------
# Process each class independently
# ------------------------------------------------------------

for cls in classes:

    cls_path = os.path.join(SOURCE_DIR, cls)

    images = [
        f for f in os.listdir(cls_path)
        if f.lower().endswith(EXTENSIONS)
    ]

    # Shuffle reproducibly
    random.shuffle(images)

    total = len(images)
    total_images += total

    # Calculate split sizes
    train_count = int(total * TRAIN_RATIO)
    val_count = int(total * VAL_RATIO)
    test_count = total - train_count - val_count

    # Split (explicit boundaries)
    train_images = images[:train_count]

    val_images = images[
        train_count:
        train_count + val_count
    ]

    test_images = images[
        train_count + val_count:
        train_count + val_count + test_count
    ]

    split_data["train"][cls] = train_images
    split_data["validation"][cls] = val_images
    split_data["test"][cls] = test_images


# ============================================================
# PRINT SPLIT SIZES
# ============================================================

train_total = sum(
    len(v) for v in split_data["train"].values()
)

val_total = sum(
    len(v) for v in split_data["validation"].values()
)

test_total = sum(
    len(v) for v in split_data["test"].values()
)

print(f"Total images collected: {total_images}")

print("\nSplit sizes:")
print(f"  Train:      {train_total} images")
print(f"  Validation: {val_total} images")
print(f"  Test:       {test_total} images")


# ============================================================
# COPY FILES
# ============================================================

print("\nCopying files...")

for split_name in ["train", "validation", "test"]:

    split_total = 0

    for cls in classes:

        images = split_data[split_name][cls]

        src_dir = os.path.join(
            SOURCE_DIR,
            cls
        )

        dst_dir = os.path.join(
            OUTPUT_DIR,
            split_name,
            cls
        )

        for img in images:

            src = os.path.join(
                src_dir,
                img
            )

            dst = os.path.join(
                dst_dir,
                img
            )

            shutil.copy2(src, dst)

        split_total += len(images)

    print(
        f"  ✅ {split_name}: "
        f"{split_total} images copied"
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL SPLIT SUMMARY")
print("=" * 70)

for split in ["train", "validation", "test"]:

    print(f"\n--- {split.upper()} ---")

    split_total = 0

    for cls in classes:

        count = len(
            split_data[split][cls]
        )

        split_total += count

        print(
            f"  {cls:30s}: "
            f"{count:>5d}"
        )

    print(
        f"  {'TOTAL':30s}: "
        f"{split_total:>5d}"
    )


# ============================================================
# FINAL CHECK
# ============================================================

print("\n" + "=" * 70)

if train_total + val_total + test_total == total_images:
    print("✅ All images accounted for.")
else:
    print("❌ ERROR: Image count mismatch!")

print("✅ Stratified 80/10/10 split complete.")
print("=" * 70)