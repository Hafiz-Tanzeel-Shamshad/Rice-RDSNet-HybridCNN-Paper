import csv
import statistics
from pathlib import Path
from collections import Counter, defaultdict

from PIL import Image


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

# ------------------------------------------------------------
# Quality thresholds
# ------------------------------------------------------------
# These are AUDIT thresholds, not automatic deletion rules.
# They flag images for manual inspection.
# ------------------------------------------------------------

MIN_WIDTH = 100
MIN_HEIGHT = 100

LOW_RESOLUTION_PIXELS = 100 * 100

VERY_SMALL_WIDTH = 64
VERY_SMALL_HEIGHT = 64

LARGE_IMAGE_PIXELS = 20_000_000

EXTREME_ASPECT_RATIO = 4.0


# ============================================================
# SETUP
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("=" * 70)
print("RICE DATASET - STEP 5: IMAGE RESOLUTION & QUALITY AUDIT")
print("=" * 70)


if not DATASET_DIR.exists():

    print(
        f"\nERROR: Dataset directory not found:"
    )

    print(DATASET_DIR)

    exit()


# ============================================================
# FIND IMAGES
# ============================================================

image_files = []

for file in DATASET_DIR.rglob("*"):

    if (
        file.is_file()
        and file.suffix.lower()
        in IMAGE_EXTENSIONS
    ):

        image_files.append(file)


print(
    f"\nTotal images found: "
    f"{len(image_files)}"
)


# ============================================================
# IMAGE ANALYSIS
# ============================================================

records = []

failed_files = []

class_statistics = defaultdict(list)

format_counts = Counter()

mode_counts = Counter()

aspect_ratio_counts = Counter()

low_resolution_images = []

very_small_images = []

extreme_aspect_ratio_images = []

very_large_images = []


print("\nAnalyzing images...")
print("-" * 70)


for index, file_path in enumerate(
    image_files,
    start=1
):

    try:

        with Image.open(file_path) as img:

            width, height = img.size

            image_format = img.format

            mode = img.mode


        # ----------------------------------------------------
        # BASIC CALCULATIONS
        # ----------------------------------------------------

        pixels = width * height

        aspect_ratio = width / height


        # ----------------------------------------------------
        # CLASS
        # ----------------------------------------------------

        try:

            class_name = file_path.parent.name

        except Exception:

            class_name = "UNKNOWN"


        # ----------------------------------------------------
        # STORE BASIC INFORMATION
        # ----------------------------------------------------

        record = {

            "file": str(file_path),

            "class": class_name,

            "width": width,

            "height": height,

            "pixels": pixels,

            "aspect_ratio": round(
                aspect_ratio,
                4
            ),

            "format": image_format,

            "mode": mode
        }


        records.append(record)


        # ----------------------------------------------------
        # CLASS STATISTICS
        # ----------------------------------------------------

        class_statistics[
            class_name
        ].append(record)


        # ----------------------------------------------------
        # FORMAT / MODE
        # ----------------------------------------------------

        format_counts[
            image_format
        ] += 1


        mode_counts[
            mode
        ] += 1


        # ----------------------------------------------------
        # ASPECT RATIO
        # ----------------------------------------------------

        aspect_category = round(
            aspect_ratio,
            1
        )

        aspect_ratio_counts[
            aspect_category
        ] += 1


        # ----------------------------------------------------
        # LOW RESOLUTION
        # ----------------------------------------------------

        if pixels < LOW_RESOLUTION_PIXELS:

            low_resolution_images.append(
                record
            )


        # ----------------------------------------------------
        # VERY SMALL DIMENSIONS
        # ----------------------------------------------------

        if (
            width < VERY_SMALL_WIDTH
            or height < VERY_SMALL_HEIGHT
        ):

            very_small_images.append(
                record
            )


        # ----------------------------------------------------
        # EXTREME ASPECT RATIO
        # ----------------------------------------------------

        if (
            aspect_ratio > EXTREME_ASPECT_RATIO
            or aspect_ratio
            < (1 / EXTREME_ASPECT_RATIO)
        ):

            extreme_aspect_ratio_images.append(
                record
            )


        # ----------------------------------------------------
        # VERY LARGE IMAGE
        # ----------------------------------------------------

        if pixels > LARGE_IMAGE_PIXELS:

            very_large_images.append(
                record
            )


    except Exception as e:

        failed_files.append({

            "file": str(file_path),

            "reason": (
                f"{type(e).__name__}: "
                f"{str(e)}"
            )
        })


    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

    if (
        index % 100 == 0
        or index == len(image_files)
    ):

        print(
            f"Processed: "
            f"{index}/{len(image_files)}"
        )


# ============================================================
# OVERALL STATISTICS
# ============================================================

widths = [
    record["width"]
    for record in records
]

heights = [
    record["height"]
    for record in records
]

pixel_counts = [
    record["pixels"]
    for record in records
]

aspect_ratios = [
    record["aspect_ratio"]
    for record in records
]


print("\n" + "=" * 70)
print("OVERALL IMAGE STATISTICS")
print("=" * 70)


if records:

    print(
        f"Valid images       : "
        f"{len(records)}"
    )

    print(
        f"Failed images      : "
        f"{len(failed_files)}"
    )

    print(
        f"Minimum width      : "
        f"{min(widths)} px"
    )

    print(
        f"Maximum width      : "
        f"{max(widths)} px"
    )

    print(
        f"Average width      : "
        f"{statistics.mean(widths):.2f} px"
    )

    print(
        f"Median width       : "
        f"{statistics.median(widths):.2f} px"
    )

    print(
        f"Minimum height     : "
        f"{min(heights)} px"
    )

    print(
        f"Maximum height     : "
        f"{max(heights)} px"
    )

    print(
        f"Average height     : "
        f"{statistics.mean(heights):.2f} px"
    )

    print(
        f"Median height      : "
        f"{statistics.median(heights):.2f} px"
    )

    print(
        f"Minimum pixels     : "
        f"{min(pixel_counts):,}"
    )

    print(
        f"Maximum pixels     : "
        f"{max(pixel_counts):,}"
    )

    print(
        f"Average pixels     : "
        f"{statistics.mean(pixel_counts):,.0f}"
    )

    print(
        f"Median pixels      : "
        f"{statistics.median(pixel_counts):,.0f}"
    )


# ============================================================
# RESOLUTION FLAGS
# ============================================================

print("\n" + "=" * 70)
print("RESOLUTION FLAGS")
print("=" * 70)


print(
    f"Low-resolution images "
    f"(< {LOW_RESOLUTION_PIXELS:,} pixels): "
    f"{len(low_resolution_images)}"
)


print(
    f"Very small images "
    f"(< {VERY_SMALL_WIDTH}x{VERY_SMALL_HEIGHT}): "
    f"{len(very_small_images)}"
)


print(
    f"Extreme aspect-ratio images: "
    f"{len(extreme_aspect_ratio_images)}"
)


print(
    f"Very large images "
    f"(> {LARGE_IMAGE_PIXELS:,} pixels): "
    f"{len(very_large_images)}"
)


# ============================================================
# FORMAT DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("IMAGE FORMAT DISTRIBUTION")
print("=" * 70)


for image_format, count in (
    format_counts.most_common()
):

    print(
        f"{str(image_format):<10} : "
        f"{count}"
    )


# ============================================================
# COLOR MODE DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("COLOR MODE DISTRIBUTION")
print("=" * 70)


for mode, count in mode_counts.most_common():

    print(
        f"{mode:<10} : "
        f"{count}"
    )


# ============================================================
# CLASS-WISE RESOLUTION
# ============================================================

print("\n" + "=" * 70)
print("CLASS-WISE RESOLUTION STATISTICS")
print("=" * 70)


print(
    f"{'Class':<30}"
    f"{'Count':>8}"
    f"{'Median W':>12}"
    f"{'Median H':>12}"
    f"{'Median Pixels':>16}"
)


print("-" * 80)


for class_name in sorted(
    class_statistics
):

    class_records = class_statistics[
        class_name
    ]


    class_widths = [
        r["width"]
        for r in class_records
    ]


    class_heights = [
        r["height"]
        for r in class_records
    ]


    class_pixels = [
        r["pixels"]
        for r in class_records
    ]


    print(
        f"{class_name:<30}"
        f"{len(class_records):>8}"
        f"{statistics.median(class_widths):>12.0f}"
        f"{statistics.median(class_heights):>12.0f}"
        f"{statistics.median(class_pixels):>16,.0f}"
    )


# ============================================================
# SAVE COMPLETE IMAGE METADATA
# ============================================================

metadata_csv = (
    OUTPUT_DIR
    / "image_quality_metadata.csv"
)


with open(
    metadata_csv,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(

        f,

        fieldnames=[
            "file",
            "class",
            "width",
            "height",
            "pixels",
            "aspect_ratio",
            "format",
            "mode"
        ]
    )

    writer.writeheader()

    writer.writerows(records)


# ============================================================
# HELPER FUNCTION FOR SAVING FLAGS
# ============================================================

def save_flagged_images(
    filename,
    data
):

    path = (
        OUTPUT_DIR
        / filename
    )


    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        if not data:

            writer = csv.writer(f)

            writer.writerow([
                "No flagged images"
            ])

            return


        fieldnames = list(
            data[0].keys()
        )


        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )


        writer.writeheader()

        writer.writerows(data)


# ============================================================
# SAVE FLAG REPORTS
# ============================================================

save_flagged_images(

    "low_resolution_images.csv",

    low_resolution_images
)


save_flagged_images(

    "very_small_images.csv",

    very_small_images
)


save_flagged_images(

    "extreme_aspect_ratio_images.csv",

    extreme_aspect_ratio_images
)


save_flagged_images(

    "very_large_images.csv",

    very_large_images
)


# ============================================================
# SAVE FAILED FILES
# ============================================================

if failed_files:

    failed_csv = (
        OUTPUT_DIR
        / "quality_analysis_failed.csv"
    )


    with open(
        failed_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(

            f,

            fieldnames=[
                "file",
                "reason"
            ]
        )


        writer.writeheader()

        writer.writerows(
            failed_files
        )


# ============================================================
# ASSESSMENT
# ============================================================

print("\n" + "=" * 70)
print("QUALITY ASSESSMENT")
print("=" * 70)


problem_count = (
    len(low_resolution_images)
    + len(very_small_images)
    + len(extreme_aspect_ratio_images)
)


if problem_count == 0:

    print(
        "✓ No obvious resolution/dimension "
        "problems detected."
    )

else:

    print(
        f"⚠️ {problem_count} "
        "potentially problematic records detected."
    )

    print(
        "These images require manual inspection."
    )


if len(mode_counts) == 1:

    print(
        "\n✓ All images use the same color mode:"
        f" {list(mode_counts.keys())[0]}"
    )

else:

    print(
        "\n⚠️ Multiple color modes detected."
    )

    print(
        "This is not automatically a problem, "
        "but preprocessing should be standardized."
    )


if len(format_counts) == 1:

    print(
        "\n✓ All images use the same image format."
    )

else:

    print(
        "\n⚠️ Multiple image formats detected."
    )

    print(
        "This is generally acceptable."
    )


# ============================================================
# IMPORTANT RESEARCH NOTE
# ============================================================

print("\n" + "=" * 70)
print("IMPORTANT RESEARCH NOTE")
print("=" * 70)


print(
    "Low resolution does NOT automatically mean "
    "an image must be removed."
)


print(
    "A 100x100 image may still contain useful "
    "disease information, depending on the task."
)


print(
    "Likewise, different resolutions are acceptable "
    "if your training pipeline resizes images consistently."
)


print(
    "Manual visual inspection is required before "
    "removing flagged images."
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("STEP 5 COMPLETE")
print("=" * 70)


print(
    "\nComplete metadata:"
    f"\n  {metadata_csv}"
)


print(
    "\nFlagged reports saved in:"
    f"\n  {OUTPUT_DIR}"
)


print(
    "\nNo images were deleted or modified."
)


print(
    "\nNext:"
    "\nSTEP 6 - Image Content Quality:"
    "\nBlur, brightness, contrast, noise, "
    "and visually suspicious images."
)