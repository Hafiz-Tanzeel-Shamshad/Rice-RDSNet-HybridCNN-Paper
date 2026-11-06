
import os
import csv
from collections import defaultdict

# Change this to your dataset's main folder path
DATASET_DIR = "./rice_leaf_disease_dataset"

# Supported image formats
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".bmp",
    ".tif", ".tiff", ".webp"
}

SPLITS = ["train", "test", "validation"]


def count_images(folder):
    """Count images in each class folder and return class-wise counts."""
    class_counts = defaultdict(int)

    if not os.path.isdir(folder):
        print(f"Warning: Folder not found: {folder}")
        return class_counts

    for root, dirs, files in os.walk(folder):
        # Ignore hidden/system folders
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d != "__MACOSX"
        ]

        for filename in files:
            if filename.startswith("."):
                continue

            extension = os.path.splitext(filename)[1].lower()

            if extension in IMAGE_EXTENSIONS:
                relative_path = os.path.relpath(root, folder)

                # Images directly inside the split folder
                # are assigned to the "Uncategorized" group.
                class_name = (
                    relative_path.split(os.sep)[0]
                    if relative_path != "."
                    else "Uncategorized"
                )

                class_counts[class_name] += 1

    return class_counts


def main():
    all_results = {}
    all_classes = set()
    split_totals = {}

    print("=" * 75)
    print("             DATASET IMAGE COUNT SUMMARY")
    print("=" * 75)

    # Count each split
    for split in SPLITS:
        split_path = os.path.join(DATASET_DIR, split)
        counts = count_images(split_path)

        all_results[split] = counts
        all_classes.update(counts.keys())
        split_totals[split] = sum(counts.values())

    # Display class-wise table
    print(f"\n{'Class Name':30} {'Train':>10} {'Test':>10} "
          f"{'Validation':>12} {'Total':>10}")
    print("-" * 75)

    for class_name in sorted(all_classes):
        train_count = all_results["train"].get(class_name, 0)
        test_count = all_results["test"].get(class_name, 0)
        val_count = all_results["validation"].get(class_name, 0)

        total = train_count + test_count + val_count

        print(f"{class_name:30} {train_count:10} {test_count:10} "
              f"{val_count:12} {total:10}")

    # Split totals
    grand_total = sum(split_totals.values())

    print("-" * 75)
    print(f"{'TOTAL IMAGES':30} "
          f"{split_totals['train']:10} "
          f"{split_totals['test']:10} "
          f"{split_totals['validation']:12} "
          f"{grand_total:10}")

    print("\n" + "=" * 75)
    print("SPLIT SUMMARY")
    print("=" * 75)

    for split in SPLITS:
        total = split_totals[split]
        percentage = (total / grand_total * 100) if grand_total else 0

        print(f"{split.capitalize():12}: {total:6} images "
              f"({percentage:.2f}%)")

    print(f"\nNumber of classes: {len(all_classes)}")
    print(f"Grand total images: {grand_total}")

    # Save class-wise summary to CSV
    csv_path = os.path.join(DATASET_DIR, "image_count_summary.csv")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Class Name", "Train Images", "Test Images",
            "Validation Images", "Total Images"
        ])

        for class_name in sorted(all_classes):
            train_count = all_results["train"].get(class_name, 0)
            test_count = all_results["test"].get(class_name, 0)
            val_count = all_results["validation"].get(class_name, 0)

            writer.writerow([
                class_name,
                train_count,
                test_count,
                val_count,
                train_count + test_count + val_count
            ])

        writer.writerow([
            "TOTAL",
            split_totals["train"],
            split_totals["test"],
            split_totals["validation"],
            grand_total
        ])

    print(f"\nCSV report saved to:\n{csv_path}")


if __name__ == "__main__":
    main()
