import os
import json
from pathlib import Path
from collections import Counter

# ============================================================
# CONFIGURATION
# ============================================================

DATASET_DIR = Path("./dataset")
OUTPUT_DIR = Path("./dataset_audit")

# Common image extensions
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp"
}

# ============================================================
# SETUP
# ============================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("RICE DATASET - STEP 1: STRUCTURE & CLASS DISTRIBUTION AUDIT")
print("=" * 70)

if not DATASET_DIR.exists():
    print(f"\nERROR: Dataset directory not found: {DATASET_DIR}")
    print("Please change DATASET_DIR in the script.")
    exit()

# ============================================================
# FIND CLASSES
# ============================================================

classes = sorted([
    folder.name
    for folder in DATASET_DIR.iterdir()
    if folder.is_dir()
])

print(f"\nDataset directory : {DATASET_DIR}")
print(f"Number of classes : {len(classes)}")

if len(classes) != 12:
    print("\nWARNING:")
    print(f"Expected 12 classes, but found {len(classes)} classes.")

# ============================================================
# ANALYZE EACH CLASS
# ============================================================

class_counts = {}
class_files = {}

all_files = []
unknown_files = []

for class_name in classes:

    class_dir = DATASET_DIR / class_name

    files = [
        file
        for file in class_dir.rglob("*")
        if file.is_file()
    ]

    image_files = [
        file
        for file in files
        if file.suffix.lower() in IMAGE_EXTENSIONS
    ]

    non_image_files = [
        file
        for file in files
        if file.suffix.lower() not in IMAGE_EXTENSIONS
    ]

    class_counts[class_name] = len(image_files)
    class_files[class_name] = [str(f) for f in image_files]

    all_files.extend(image_files)
    unknown_files.extend(non_image_files)

# ============================================================
# BASIC STATISTICS
# ============================================================

total_images = sum(class_counts.values())

if total_images == 0:
    print("\nERROR: No images found.")
    exit()

max_class = max(class_counts, key=class_counts.get)
min_class = min(class_counts, key=class_counts.get)

max_count = class_counts[max_class]
min_count = class_counts[min_class]

imbalance_ratio = max_count / min_count

# ============================================================
# PRINT CLASS DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("CLASS DISTRIBUTION")
print("=" * 70)

print(
    f"{'Class':<30}"
    f"{'Images':>10}"
    f"{'Percentage':>15}"
)

print("-" * 70)

for class_name in sorted(
    class_counts,
    key=class_counts.get,
    reverse=True
):

    count = class_counts[class_name]
    percentage = (count / total_images) * 100

    print(
        f"{class_name:<30}"
        f"{count:>10}"
        f"{percentage:>14.2f}%"
    )

# ============================================================
# IMBALANCE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("CLASS IMBALANCE ANALYSIS")
print("=" * 70)

print(f"Maximum class : {max_class} ({max_count})")
print(f"Minimum class : {min_class} ({min_count})")
print(f"Imbalance ratio: {imbalance_ratio:.2f}:1")

if imbalance_ratio <= 2:
    print("Assessment: Low imbalance")

elif imbalance_ratio <= 5:
    print("Assessment: Moderate imbalance")

elif imbalance_ratio <= 10:
    print("Assessment: High imbalance")

else:
    print("Assessment: Severe imbalance")

# ============================================================
# EMPTY CLASSES
# ============================================================

empty_classes = [
    class_name
    for class_name, count in class_counts.items()
    if count == 0
]

if empty_classes:

    print("\nWARNING - EMPTY CLASSES:")
    for class_name in empty_classes:
        print(f"  - {class_name}")

else:
    print("\nNo empty classes found.")

# ============================================================
# NON-IMAGE FILES
# ============================================================

print("\n" + "=" * 70)
print("NON-IMAGE FILE CHECK")
print("=" * 70)

if unknown_files:

    print(f"Found {len(unknown_files)} non-image files.")

    for file in unknown_files[:20]:
        print(f"  {file}")

    if len(unknown_files) > 20:
        print(
            f"  ... and "
            f"{len(unknown_files) - 20} more."
        )

else:

    print("No unexpected non-image files found.")

# ============================================================
# FILE EXTENSION ANALYSIS
# ============================================================

extension_counts = Counter(
    file.suffix.lower()
    for file in all_files
)

print("\n" + "=" * 70)
print("IMAGE FILE EXTENSIONS")
print("=" * 70)

for extension, count in extension_counts.most_common():

    print(
        f"{extension:<10} : {count:>8}"
    )

# ============================================================
# DATASET SUMMARY
# ============================================================

summary = {

    "dataset_directory": str(DATASET_DIR),

    "number_of_classes": len(classes),

    "classes": classes,

    "total_images": total_images,

    "class_counts": class_counts,

    "largest_class": {
        "name": max_class,
        "count": max_count
    },

    "smallest_class": {
        "name": min_class,
        "count": min_count
    },

    "imbalance_ratio": round(
        imbalance_ratio,
        4
    ),

    "image_extensions": dict(
        extension_counts
    ),

    "non_image_files": len(
        unknown_files
    )
}

# ============================================================
# SAVE JSON REPORT
# ============================================================

report_path = OUTPUT_DIR / "step01_dataset_summary.json"

with open(
    report_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        summary,
        f,
        indent=4
    )

# ============================================================
# SAVE CLASS COUNTS CSV
# ============================================================

csv_path = OUTPUT_DIR / "class_distribution.csv"

with open(
    csv_path,
    "w",
    encoding="utf-8"
) as f:

    f.write("class,count,percentage\n")

    for class_name in sorted(class_counts):

        count = class_counts[class_name]
        percentage = (
            count / total_images
        ) * 100

        f.write(
            f'"{class_name}",'
            f"{count},"
            f"{percentage:.4f}\n"
        )

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("STEP 1 COMPLETE")
print("=" * 70)

print(f"Total images      : {total_images}")
print(f"Total classes     : {len(classes)}")
print(f"Imbalance ratio   : {imbalance_ratio:.2f}:1")
print(f"JSON report       : {report_path}")
print(f"CSV report        : {csv_path}")

print("\nNext step:")
print("Run Step 2 - Corrupted / Unreadable Image Detection.")