"""
Rice Leaf Disease Dataset - Oversampling Script
================================================
This script performs targeted oversampling of the three minority classes
(ragged_stunt_virus, sheath_rot, stem_rot) to bring them to 350 images each.

Techniques used:
    1. ShiftScaleRotate  (Shift ±8%, Scale ±10%, Rotate ±20°)
    2. HorizontalFlip    (p=0.5)
    3. RandomBrightnessContrast (Brightness ±12%, Contrast ±12%)
    4. Resize            (224 × 224)

Author: [Your Name]
Date:   2026
"""

import os
import random
import time
import cv2
import numpy as np
import albumentations as A

# ============================================================
# CONFIGURATION
# ============================================================
DATASET_DIR = "./dataset"           # Local machine
# DATASET_DIR = "/content/drive/MyDrive/dataset"  # Uncomment for Colab

TARGET = 350

MINORITY_CLASSES = [
    "ragged_stunt_virus",
    "sheath_rot",
    "stem_rot"
]

# ============================================================
# AUGMENTATION PIPELINE
# ============================================================
# Technique 1: ShiftScaleRotate (Shift + Scale + Rotate)
# Technique 2: HorizontalFlip
# Technique 3: RandomBrightnessContrast (Brightness + Contrast)
# Technique 4: Resize (final size)
# ============================================================
transform = A.Compose([
    # ---- Technique 1: Combined Geometric Transform ----
    A.ShiftScaleRotate(
        shift_limit=0.08,                    # ±8% translation
        scale_limit=0.10,                    # ±10% zoom
        rotate_limit=20,                     # ±20° rotation
        border_mode=cv2.BORDER_REFLECT_101,  # Reflect border pixels
        p=0.7
    ),

    # ---- Technique 2: Horizontal Flip ----
    A.HorizontalFlip(p=0.5),

    # ---- Technique 3: Photometric Transform ----
    A.RandomBrightnessContrast(
        brightness_limit=0.12,               # ±12% brightness
        contrast_limit=0.12,                 # ±12% contrast
        p=0.5
    ),

    # ---- Technique 4: Final Resize ----
    A.Resize(224, 224)
])

# ============================================================
# REPRODUCIBILITY
# ============================================================
random.seed(42)
np.random.seed(42)

# ============================================================
# OVERSAMPLING
# ============================================================
print("=" * 70)
print("RICE LEAF DATASET — OVERSAMPLING MINORITY CLASSES")
print("=" * 70)
print(f"Target per minority class: {TARGET}")
print(f"Minority classes: {MINORITY_CLASSES}")
print("=" * 70)

extensions = (".jpg", ".jpeg", ".png", ".jfif", ".webp")

# Store results
results = {}

for cls in MINORITY_CLASSES:
    cls_path = os.path.join(DATASET_DIR, cls)

    if not os.path.exists(cls_path):
        print(f"❌ Folder not found: {cls_path}")
        continue

    # Original images (without 'aug_' prefix)
    original_images = [
        f for f in os.listdir(cls_path)
        if f.lower().endswith(extensions) and not f.startswith("aug_")
    ]

    current = len(original_images)
    needed = TARGET - current

    if needed <= 0:
        print(f"\n✅ {cls}: {current} (already ≥ {TARGET}) — skipping")
        results[cls] = {"original": current, "added": 0, "final": current}
        continue

    print(f"\n📂 {cls}")
    print(f"   Original images: {current}")
    print(f"   Augmented needed: {needed}")

    count = 0
    attempts = 0
    max_attempts = needed * 5  # Safety limit

    while count < needed and attempts < max_attempts:
        attempts += 1

        # Random original image
        img_name = random.choice(original_images)
        img_path = os.path.join(cls_path, img_name)

        # Read image (OpenCV returns BGR)
        image = cv2.imread(img_path)

        if image is None:
            print(f"   ⚠️ Could not read: {img_path}")
            continue

        # Convert BGR → RGB (Albumentations expects RGB)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        try:
            # Apply augmentation pipeline
            augmented = transform(image=image)
            aug_image = augmented["image"]

            # Convert RGB → BGR (OpenCV writes BGR)
            aug_image = cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR)

            # Unique filename with timestamp to prevent overwrite
            timestamp = int(time.time() * 1000) % 1000000
            output_name = f"aug_{timestamp:06d}_{count + 1:04d}.jpg"
            output_path = os.path.join(cls_path, output_name)

            # Save with high JPEG quality
            cv2.imwrite(
                output_path,
                aug_image,
                [cv2.IMWRITE_JPEG_QUALITY, 95]
            )

            count += 1

            if count % 50 == 0:
                print(f"   → Progress: {count}/{needed}")

        except Exception as e:
            print(f"   Error: {img_path} → {e}")

    # Final count
    final_count = len([
        f for f in os.listdir(cls_path)
        if f.lower().endswith(extensions)
    ])

    print(f"   ✅ Final count: {final_count}")

    results[cls] = {
        "original": current,
        "added": count,
        "final": final_count
    }

print("\n" + "=" * 70)
print("OVERSAMPLING COMPLETE")
print("=" * 70)

# ============================================================
# FINAL DATASET SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("FINAL DATASET SUMMARY")
print("=" * 70)

total = 0
class_counts = {}

for cls in sorted(os.listdir(DATASET_DIR)):
    cls_path = os.path.join(DATASET_DIR, cls)
    if os.path.isdir(cls_path):
        count = len([
            f for f in os.listdir(cls_path)
            if f.lower().endswith(extensions)
        ])
        class_counts[cls] = count
        total += count
        print(f"  {cls:30s}: {count:>5d}")

print("-" * 70)
print(f"  {'TOTAL':30s}: {total:>5d}")
print("=" * 70)

# ============================================================
# IMBALANCE CHECK
# ============================================================
if class_counts:
    max_c = max(class_counts.values())
    min_c = min(class_counts.values())
    print(f"\n  Max class size: {max_c}")
    print(f"  Min class size: {min_c}")
    print(f"  Imbalance ratio: {max_c/min_c:.2f}:1")

print("\n" + "=" * 70)
print("DONE.")
print("=" * 70)