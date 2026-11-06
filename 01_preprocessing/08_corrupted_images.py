import os
import csv
from pathlib import Path
from PIL import Image, UnidentifiedImageError

# ============================================================
# CONFIGURATION
# ============================================================

DATASET_DIR = Path("./dataset")
OUTPUT_DIR = Path("./dataset_audit")

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
print("RICE DATASET - STEP 2: CORRUPTED IMAGE AUDIT")
print("=" * 70)

if not DATASET_DIR.exists():
    print(f"\nERROR: Dataset directory not found:")
    print(DATASET_DIR)
    exit()

# ============================================================
# FIND ALL IMAGES
# ============================================================

image_files = []

for file in DATASET_DIR.rglob("*"):

    if (
        file.is_file()
        and file.suffix.lower() in IMAGE_EXTENSIONS
    ):
        image_files.append(file)

print(f"\nTotal image files found: {len(image_files)}")

# ============================================================
# CHECK IMAGES
# ============================================================

valid_images = []
corrupted_images = []

print("\nChecking images...")
print("-" * 70)

for index, file_path in enumerate(image_files, start=1):

    try:

        # First check: open image
        with Image.open(file_path) as img:

            # Force PIL to verify the file structure
            img.verify()

        # Second check:
        # Actually load image data.
        # This catches some truncated/corrupt files
        # that verify() alone may not detect.

        with Image.open(file_path) as img:

            img.load()

            width, height = img.size
            image_format = img.format
            mode = img.mode

        # Check for invalid dimensions
        if width <= 0 or height <= 0:

            corrupted_images.append({
                "file": str(file_path),
                "reason": "Invalid image dimensions",
                "width": width,
                "height": height,
                "format": image_format,
                "mode": mode
            })

            continue

        valid_images.append({
            "file": str(file_path),
            "width": width,
            "height": height,
            "format": image_format,
            "mode": mode
        })

    except UnidentifiedImageError:

        corrupted_images.append({
            "file": str(file_path),
            "reason": "PIL could not identify image",
            "width": "",
            "height": "",
            "format": "",
            "mode": ""
        })

    except Exception as e:

        corrupted_images.append({
            "file": str(file_path),
            "reason": f"{type(e).__name__}: {str(e)}",
            "width": "",
            "height": "",
            "format": "",
            "mode": ""
        })

    # Progress
    if index % 100 == 0 or index == len(image_files):

        print(
            f"Checked: {index}/{len(image_files)}"
        )

# ============================================================
# RESULTS
# ============================================================

total = len(image_files)
valid = len(valid_images)
corrupted = len(corrupted_images)

if total > 0:
    corrupted_percentage = (
        corrupted / total
    ) * 100
else:
    corrupted_percentage = 0

print("\n" + "=" * 70)
print("CORRUPTED IMAGE RESULTS")
print("=" * 70)

print(f"Total images       : {total}")
print(f"Valid images       : {valid}")
print(f"Corrupted images   : {corrupted}")
print(
    f"Corrupted percent  : "
    f"{corrupted_percentage:.2f}%"
)

# ============================================================
# ASSESSMENT
# ============================================================

print("\n" + "=" * 70)
print("ASSESSMENT")
print("=" * 70)

if corrupted == 0:

    print("✓ Excellent: No corrupted images detected.")

elif corrupted_percentage < 1:

    print(
        "⚠️ Very small number of corrupted images detected."
    )

elif corrupted_percentage < 5:

    print(
        "⚠️ Some corrupted images detected."
    )
    print(
        "Review and remove/replace them before training."
    )

else:

    print(
        "❌ Significant number of corrupted images detected."
    )
    print(
        "Dataset should be cleaned before model training."
    )

# ============================================================
# SAVE CORRUPTED IMAGE REPORT
# ============================================================

corrupted_csv = (
    OUTPUT_DIR / "corrupted_images.csv"
)

with open(
    corrupted_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "file",
            "reason",
            "width",
            "height",
            "format",
            "mode"
        ]
    )

    writer.writeheader()

    writer.writerows(
        corrupted_images
    )

# ============================================================
# SAVE VALID IMAGE INFORMATION
# ============================================================

valid_csv = (
    OUTPUT_DIR / "valid_images_metadata.csv"
)

with open(
    valid_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "file",
            "width",
            "height",
            "format",
            "mode"
        ]
    )

    writer.writeheader()

    writer.writerows(
        valid_images
    )

# ============================================================
# PRINT CORRUPTED FILES
# ============================================================

if corrupted_images:

    print("\n" + "=" * 70)
    print("CORRUPTED / UNREADABLE FILES")
    print("=" * 70)

    for item in corrupted_images:

        print(
            f"\nFile   : {item['file']}"
        )

        print(
            f"Reason : {item['reason']}"
        )

else:

    print("\nNo corrupted or unreadable images found.")

# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("STEP 2 COMPLETE")
print("=" * 70)

print(f"Report saved to:")
print(f"  {corrupted_csv}")

print(f"\nValid image metadata saved to:")
print(f"  {valid_csv}")

print("\nIMPORTANT:")
print("No files were deleted or modified.")
print("Review the CSV before removing any problematic images.")