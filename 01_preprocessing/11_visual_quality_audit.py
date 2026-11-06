import csv
import math
from pathlib import Path
from collections import Counter, defaultdict

import cv2
import numpy as np


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
# VISUAL QUALITY THRESHOLDS
# ============================================================
#
# These are FLAGGING thresholds.
# They are NOT automatic deletion rules.
#
# You must manually inspect flagged images.
# ============================================================

# Laplacian variance:
# Lower value generally means more blur.
BLUR_THRESHOLD = 50

# Mean grayscale intensity:
# 0   = black
# 255 = white
DARK_THRESHOLD = 35
BRIGHT_THRESHOLD = 220

# Standard deviation of grayscale intensity.
# Very low value means the image has very little contrast.
LOW_CONTRAST_THRESHOLD = 20

# Percentage of pixels close to black/white.
EXTREME_PIXEL_PERCENTAGE = 0.70

# Entropy threshold.
# Very low entropy can indicate blank/uninformative images.
LOW_ENTROPY_THRESHOLD = 3.0


# ============================================================
# SETUP
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("=" * 70)
print("RICE DATASET - STEP 6: VISUAL IMAGE QUALITY AUDIT")
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
# HELPER FUNCTIONS
# ============================================================

def calculate_entropy(gray_image):
    """
    Calculate Shannon entropy of a grayscale image.

    Higher entropy generally indicates more variation
    and visual information.
    """

    histogram = cv2.calcHist(
        [gray_image],
        [0],
        None,
        [256],
        [0, 256]
    )

    histogram = histogram.ravel()

    total = histogram.sum()

    if total == 0:
        return 0.0

    probabilities = histogram / total

    probabilities = probabilities[
        probabilities > 0
    ]

    entropy = -np.sum(
        probabilities
        * np.log2(probabilities)
    )

    return float(entropy)


def analyze_image(file_path):

    image = cv2.imread(
        str(file_path),
        cv2.IMREAD_COLOR
    )

    if image is None:

        raise ValueError(
            "OpenCV could not read image"
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------------
    # Brightness
    # --------------------------------------------------------

    mean_brightness = float(
        np.mean(gray)
    )

    # --------------------------------------------------------
    # Contrast
    # --------------------------------------------------------

    contrast = float(
        np.std(gray)
    )

    # --------------------------------------------------------
    # Sharpness / Blur
    # --------------------------------------------------------
    #
    # Variance of Laplacian is a common
    # blur/sharpness indicator.
    # --------------------------------------------------------

    sharpness = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    # --------------------------------------------------------
    # Dark Pixels
    # --------------------------------------------------------

    dark_pixels = np.mean(
        gray < 20
    )

    # --------------------------------------------------------
    # Bright Pixels
    # --------------------------------------------------------

    bright_pixels = np.mean(
        gray > 235
    )

    # --------------------------------------------------------
    # Entropy
    # --------------------------------------------------------

    entropy = calculate_entropy(
        gray
    )

    return {

        "brightness": mean_brightness,

        "contrast": contrast,

        "sharpness": sharpness,

        "dark_pixel_ratio": float(
            dark_pixels
        ),

        "bright_pixel_ratio": float(
            bright_pixels
        ),

        "entropy": entropy
    }


# ============================================================
# ANALYSIS
# ============================================================

records = []

failed_files = []

flagged_blur = []

flagged_dark = []

flagged_bright = []

flagged_low_contrast = []

flagged_extreme_pixels = []

flagged_low_entropy = []

flagged_multiple_issues = []


print("\nAnalyzing visual quality...")
print("-" * 70)


for index, file_path in enumerate(
    image_files,
    start=1
):

    try:

        metrics = analyze_image(
            file_path
        )

        # ----------------------------------------------------
        # CLASS
        # ----------------------------------------------------

        class_name = file_path.parent.name

        # ----------------------------------------------------
        # FLAGS
        # ----------------------------------------------------

        flags = []

        # Blur
        if (
            metrics["sharpness"]
            < BLUR_THRESHOLD
        ):

            flags.append(
                "possible_blur"
            )

        # Dark
        if (
            metrics["brightness"]
            < DARK_THRESHOLD
        ):

            flags.append(
                "very_dark"
            )

        # Bright
        if (
            metrics["brightness"]
            > BRIGHT_THRESHOLD
        ):

            flags.append(
                "very_bright"
            )

        # Low contrast
        if (
            metrics["contrast"]
            < LOW_CONTRAST_THRESHOLD
        ):

            flags.append(
                "low_contrast"
            )

        # Extreme pixels
        if (
            metrics["dark_pixel_ratio"]
            > EXTREME_PIXEL_PERCENTAGE
            or
            metrics["bright_pixel_ratio"]
            > EXTREME_PIXEL_PERCENTAGE
        ):

            flags.append(
                "extreme_pixels"
            )

        # Low entropy
        if (
            metrics["entropy"]
            < LOW_ENTROPY_THRESHOLD
        ):

            flags.append(
                "low_entropy"
            )

        # ----------------------------------------------------
        # RECORD
        # ----------------------------------------------------

        record = {

            "file": str(file_path),

            "class": class_name,

            "brightness": round(
                metrics["brightness"],
                4
            ),

            "contrast": round(
                metrics["contrast"],
                4
            ),

            "sharpness": round(
                metrics["sharpness"],
                4
            ),

            "dark_pixel_ratio": round(
                metrics["dark_pixel_ratio"],
                4
            ),

            "bright_pixel_ratio": round(
                metrics["bright_pixel_ratio"],
                4
            ),

            "entropy": round(
                metrics["entropy"],
                4
            ),

            "flags": ";".join(flags)
        }

        records.append(
            record
        )

        # ----------------------------------------------------
        # STORE INDIVIDUAL FLAGS
        # ----------------------------------------------------

        if "possible_blur" in flags:

            flagged_blur.append(
                record
            )

        if "very_dark" in flags:

            flagged_dark.append(
                record
            )

        if "very_bright" in flags:

            flagged_bright.append(
                record
            )

        if "low_contrast" in flags:

            flagged_low_contrast.append(
                record
            )

        if "extreme_pixels" in flags:

            flagged_extreme_pixels.append(
                record
            )

        if "low_entropy" in flags:

            flagged_low_entropy.append(
                record
            )

        if len(flags) >= 2:

            flagged_multiple_issues.append(
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
# RESULTS
# ============================================================

print("\n" + "=" * 70)
print("VISUAL QUALITY RESULTS")
print("=" * 70)


print(
    f"Successfully analyzed : "
    f"{len(records)}"
)

print(
    f"Failed images         : "
    f"{len(failed_files)}"
)

print(
    f"Possible blurry       : "
    f"{len(flagged_blur)}"
)

print(
    f"Very dark             : "
    f"{len(flagged_dark)}"
)

print(
    f"Very bright           : "
    f"{len(flagged_bright)}"
)

print(
    f"Low contrast          : "
    f"{len(flagged_low_contrast)}"
)

print(
    f"Extreme pixels        : "
    f"{len(flagged_extreme_pixels)}"
)

print(
    f"Low entropy           : "
    f"{len(flagged_low_entropy)}"
)

print(
    f"Multiple issues       : "
    f"{len(flagged_multiple_issues)}"
)


# ============================================================
# CLASS-WISE FLAG ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("CLASS-WISE VISUAL QUALITY")
print("=" * 70)


class_data = defaultdict(list)

for record in records:

    class_data[
        record["class"]
    ].append(record)


print(
    f"{'Class':<30}"
    f"{'Images':>8}"
    f"{'Blur':>8}"
    f"{'Dark':>8}"
    f"{'Bright':>8}"
    f"{'LowCtr':>8}"
)


print("-" * 78)


for class_name in sorted(
    class_data
):

    class_records = class_data[
        class_name
    ]

    blur_count = sum(
        "possible_blur"
        in r["flags"]
        for r in class_records
    )

    dark_count = sum(
        "very_dark"
        in r["flags"]
        for r in class_records
    )

    bright_count = sum(
        "very_bright"
        in r["flags"]
        for r in class_records
    )

    low_contrast_count = sum(
        "low_contrast"
        in r["flags"]
        for r in class_records
    )

    print(
        f"{class_name:<30}"
        f"{len(class_records):>8}"
        f"{blur_count:>8}"
        f"{dark_count:>8}"
        f"{bright_count:>8}"
        f"{low_contrast_count:>8}"
    )


# ============================================================
# SUMMARY STATISTICS
# ============================================================

if records:

    brightness_values = [
        r["brightness"]
        for r in records
    ]

    contrast_values = [
        r["contrast"]
        for r in records
    ]

    sharpness_values = [
        r["sharpness"]
        for r in records
    ]

    entropy_values = [
        r["entropy"]
        for r in records
    ]

    print("\n" + "=" * 70)
    print("METRIC SUMMARY")
    print("=" * 70)

    print(
        f"Brightness:"
        f"\n  Min    : "
        f"{min(brightness_values):.2f}"
        f"\n  Mean   : "
        f"{np.mean(brightness_values):.2f}"
        f"\n  Median : "
        f"{np.median(brightness_values):.2f}"
        f"\n  Max    : "
        f"{max(brightness_values):.2f}"
    )

    print(
        f"\nContrast:"
        f"\n  Min    : "
        f"{min(contrast_values):.2f}"
        f"\n  Mean   : "
        f"{np.mean(contrast_values):.2f}"
        f"\n  Median : "
        f"{np.median(contrast_values):.2f}"
        f"\n  Max    : "
        f"{max(contrast_values):.2f}"
    )

    print(
        f"\nSharpness:"
        f"\n  Min    : "
        f"{min(sharpness_values):.2f}"
        f"\n  Mean   : "
        f"{np.mean(sharpness_values):.2f}"
        f"\n  Median : "
        f"{np.median(sharpness_values):.2f}"
        f"\n  Max    : "
        f"{max(sharpness_values):.2f}"
    )

    print(
        f"\nEntropy:"
        f"\n  Min    : "
        f"{min(entropy_values):.2f}"
        f"\n  Mean   : "
        f"{np.mean(entropy_values):.2f}"
        f"\n  Median : "
        f"{np.median(entropy_values):.2f}"
        f"\n  Max    : "
        f"{max(entropy_values):.2f}"
    )


# ============================================================
# SAVE COMPLETE REPORT
# ============================================================

metadata_csv = (
    OUTPUT_DIR
    / "visual_quality_metadata.csv"
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
            "brightness",
            "contrast",
            "sharpness",
            "dark_pixel_ratio",
            "bright_pixel_ratio",
            "entropy",
            "flags"
        ]
    )

    writer.writeheader()

    writer.writerows(records)


# ============================================================
# SAVE FLAGGED IMAGES
# ============================================================

def save_report(
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


save_report(
    "flagged_blurry_images.csv",
    flagged_blur
)

save_report(
    "flagged_dark_images.csv",
    flagged_dark
)

save_report(
    "flagged_bright_images.csv",
    flagged_bright
)

save_report(
    "flagged_low_contrast_images.csv",
    flagged_low_contrast
)

save_report(
    "flagged_extreme_pixel_images.csv",
    flagged_extreme_pixels
)

save_report(
    "flagged_low_entropy_images.csv",
    flagged_low_entropy
)

save_report(
    "flagged_multiple_issues.csv",
    flagged_multiple_issues
)


# ============================================================
# SAVE FAILED FILES
# ============================================================

if failed_files:

    failed_csv = (
        OUTPUT_DIR
        / "visual_quality_failed.csv"
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

total_flagged = len(
    set(
        r["file"]
        for r in (
            flagged_blur
            + flagged_dark
            + flagged_bright
            + flagged_low_contrast
            + flagged_extreme_pixels
            + flagged_low_entropy
        )
    )
)


print("\n" + "=" * 70)
print("ASSESSMENT")
print("=" * 70)


print(
    f"Unique flagged images: "
    f"{total_flagged}"
)


if total_flagged == 0:

    print(
        "✓ No obvious visual-quality issues detected."
    )

elif total_flagged < 0.05 * len(records):

    print(
        "✓ Less than 5% of images were flagged."
    )

    print(
        "Manual inspection is still recommended."
    )

elif total_flagged < 0.15 * len(records):

    print(
        "⚠️ Between 5% and 15% of images were flagged."
    )

    print(
        "Review the flagged images carefully."
    )

else:

    print(
        "⚠️ More than 15% of images were flagged."
    )

    print(
        "The dataset may have substantial visual-quality issues."
    )


# ============================================================
# IMPORTANT RESEARCH NOTE
# ============================================================

print("\n" + "=" * 70)
print("IMPORTANT RESEARCH NOTE")
print("=" * 70)


print(
    "These metrics are screening indicators, "
    "NOT proof that an image is bad."
)


print(
    "For example, a naturally dark rice-leaf image "
    "may still be scientifically useful."
)


print(
    "Similarly, a low sharpness score may occur "
    "because of natural texture or image acquisition."
)


print(
    "Manually inspect flagged images before removal."
)


print(
    "Do NOT automatically delete all flagged images."
)


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("STEP 6 COMPLETE")
print("=" * 70)


print(
    "\nComplete report:"
    f"\n  {metadata_csv}"
)


print(
    "\nFlag reports saved inside:"
    f"\n  {OUTPUT_DIR}"
)


print(
    "\nNo images were deleted or modified."
)


print(
    "\nNext:"
    "\nSTEP 7 - Source/Dataset Origin Analysis"
    "\nfor your multiple Kaggle datasets."
)