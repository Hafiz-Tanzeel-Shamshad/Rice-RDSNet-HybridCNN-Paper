import hashlib
import csv
from pathlib import Path
from collections import defaultdict

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
print("RICE DATASET - STEP 3: EXACT DUPLICATE DETECTION")
print("=" * 70)

if not DATASET_DIR.exists():
    print(f"\nERROR: Dataset directory not found:")
    print(DATASET_DIR)
    exit()

# ============================================================
# MD5 HASH FUNCTION
# ============================================================

def calculate_md5(file_path, chunk_size=1024 * 1024):
    """
    Calculate MD5 hash of a file.

    The file is read in chunks to avoid loading
    large files completely into memory.
    """

    md5 = hashlib.md5()

    try:

        with open(file_path, "rb") as f:

            while True:

                chunk = f.read(chunk_size)

                if not chunk:
                    break

                md5.update(chunk)

        return md5.hexdigest()

    except Exception as e:

        print(
            f"\nERROR reading file: {file_path}"
        )

        print(
            f"Reason: {e}"
        )

        return None


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

print(
    f"\nTotal image files found: "
    f"{len(image_files)}"
)

# ============================================================
# CALCULATE HASHES
# ============================================================

hash_to_files = defaultdict(list)

failed_files = []

print("\nCalculating MD5 hashes...")
print("-" * 70)

for index, file_path in enumerate(
    image_files,
    start=1
):

    file_hash = calculate_md5(file_path)

    if file_hash is None:

        failed_files.append(
            str(file_path)
        )

        continue

    hash_to_files[file_hash].append(
        file_path
    )

    if (
        index % 100 == 0
        or index == len(image_files)
    ):

        print(
            f"Processed: "
            f"{index}/{len(image_files)}"
        )

# ============================================================
# FIND DUPLICATES
# ============================================================

duplicate_groups = []

for file_hash, files in hash_to_files.items():

    if len(files) > 1:

        duplicate_groups.append({
            "hash": file_hash,
            "files": files
        })

# ============================================================
# STATISTICS
# ============================================================

total_duplicate_groups = len(
    duplicate_groups
)

duplicate_file_count = sum(
    len(group["files"])
    for group in duplicate_groups
)

# Number of extra copies beyond the first copy
redundant_files = sum(
    len(group["files"]) - 1
    for group in duplicate_groups
)

total_images = len(image_files)

if total_images > 0:

    duplicate_percentage = (
        duplicate_file_count
        / total_images
    ) * 100

else:

    duplicate_percentage = 0

# ============================================================
# PRINT RESULTS
# ============================================================

print("\n" + "=" * 70)
print("EXACT DUPLICATE RESULTS")
print("=" * 70)

print(
    f"Total images              : "
    f"{total_images}"
)

print(
    f"Unique image hashes       : "
    f"{len(hash_to_files)}"
)

print(
    f"Duplicate groups          : "
    f"{total_duplicate_groups}"
)

print(
    f"Files involved in duplicates: "
    f"{duplicate_file_count}"
)

print(
    f"Redundant copies          : "
    f"{redundant_files}"
)

print(
    f"Duplicate file percentage : "
    f"{duplicate_percentage:.2f}%"
)

# ============================================================
# ASSESSMENT
# ============================================================

print("\n" + "=" * 70)
print("ASSESSMENT")
print("=" * 70)

if total_duplicate_groups == 0:

    print(
        "✓ Excellent: No exact duplicate images detected."
    )

elif duplicate_percentage < 1:

    print(
        "⚠️ Very few exact duplicates detected."
    )

elif duplicate_percentage < 5:

    print(
        "⚠️ Some exact duplicates detected."
    )

else:

    print(
        "❌ Significant exact duplication detected."
    )

    print(
        "The dataset should be investigated before training."
    )

# ============================================================
# SHOW DUPLICATE GROUPS
# ============================================================

if duplicate_groups:

    print("\n" + "=" * 70)
    print("DUPLICATE GROUPS")
    print("=" * 70)

    for group_number, group in enumerate(
        duplicate_groups,
        start=1
    ):

        print(
            f"\nDuplicate Group #{group_number}"
        )

        print(
            f"MD5: {group['hash']}"
        )

        for file_path in group["files"]:

            print(
                f"  {file_path}"
            )

# ============================================================
# SAVE DUPLICATE REPORT
# ============================================================

duplicate_csv = (
    OUTPUT_DIR
    / "exact_duplicates.csv"
)

with open(
    duplicate_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "duplicate_group",
        "md5_hash",
        "file"
    ])

    for group_number, group in enumerate(
        duplicate_groups,
        start=1
    ):

        for file_path in group["files"]:

            writer.writerow([
                group_number,
                group["hash"],
                str(file_path)
            ])

# ============================================================
# SAVE HASH DATABASE
# ============================================================

hash_csv = (
    OUTPUT_DIR
    / "image_md5_hashes.csv"
)

with open(
    hash_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "md5_hash",
        "file"
    ])

    for file_hash, files in hash_to_files.items():

        for file_path in files:

            writer.writerow([
                file_hash,
                str(file_path)
            ])

# ============================================================
# SAVE FAILED FILES
# ============================================================

if failed_files:

    failed_csv = (
        OUTPUT_DIR
        / "hash_failed_files.csv"
    )

    with open(
        failed_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "file"
        ])

        for file_path in failed_files:

            writer.writerow([
                file_path
            ])

# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("STEP 3 COMPLETE")
print("=" * 70)

print(
    f"\nDuplicate report:"
    f"\n  {duplicate_csv}"
)

print(
    f"\nHash database:"
    f"\n  {hash_csv}"
)

if failed_files:

    print(
        f"\n⚠️ Hash calculation failed for "
        f"{len(failed_files)} files."
    )

print("\nIMPORTANT:")
print(
    "No images were deleted or modified."
)

print(
    "\nNext step:"
)

print(
    "STEP 4 - Near-Duplicate Detection"
)