import os
import hashlib
from collections import defaultdict
from PIL import Image

# ============================================================
# CONFIGURATION
# ============================================================
DATASET_DIR = './dataset'   # <-- apna path yahan

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def md5_hash(filepath, chunk_size=8192):
    """Return MD5 hash of a file."""
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def get_all_images(folder):
    """Return list of all image paths in folder (recursive)."""
    images = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif', '.webp')):
                images.append(os.path.join(root, f))
    return images

def get_class_from_path(path, base_dir):
    """Get class name from path (first subfolder under base_dir)."""
    rel = os.path.relpath(path, base_dir)
    parts = rel.split(os.sep)
    return parts[0] if parts else 'unknown'

# ============================================================
# STEP 1: COLLECT ALL IMAGES
# ============================================================
print("=" * 70)
print("STEP 1: COLLECTING ALL IMAGES")
print("=" * 70)

all_images = get_all_images(DATASET_DIR)
print(f"Total images found: {len(all_images)}")

# Per-class count
class_counts = defaultdict(int)
for path in all_images:
    cls = get_class_from_path(path, DATASET_DIR)
    class_counts[cls] += 1

print("\nPer-class counts:")
for cls in sorted(class_counts.keys()):
    print(f"  {cls:30s}: {class_counts[cls]}")

# ============================================================
# STEP 2: COMPUTE MD5 HASHES
# ============================================================
print("\n" + "=" * 70)
print("STEP 2: COMPUTING MD5 HASHES (may take a few minutes)")
print("=" * 70)

hash_to_paths = defaultdict(list)

for i, path in enumerate(all_images, 1):
    if i % 500 == 0:
        print(f"  Processed {i}/{len(all_images)}...")
    try:
        h = md5_hash(path)
        hash_to_paths[h].append(path)
    except Exception as e:
        print(f"  Error hashing {path}: {e}")

print(f"\nUnique hashes: {len(hash_to_paths)}")
print(f"Total images: {len(all_images)}")

# ============================================================
# STEP 3: FIND DUPLICATES
# ============================================================
print("\n" + "=" * 70)
print("STEP 3: DUPLICATE ANALYSIS")
print("=" * 70)

duplicates = {h: paths for h, paths in hash_to_paths.items() if len(paths) > 1}

total_extra = sum(len(paths) - 1 for paths in duplicates.values())
print(f"Duplicate groups (same image, multiple copies): {len(duplicates)}")
print(f"Total extra (redundant) images: {total_extra}")

# ============================================================
# STEP 4: DUPLICATES BY CLASS
# ============================================================
print("\n" + "=" * 70)
print("STEP 4: DUPLICATES BY CLASS")
print("=" * 70)

dupes_by_class = defaultdict(int)
cross_class_dupes = []

for h, paths in duplicates.items():
    classes = [get_class_from_path(p, DATASET_DIR) for p in paths]
    
    if len(set(classes)) > 1:
        cross_class_dupes.append((h, paths))
    
    for cls in classes:
        dupes_by_class[cls] += 1

print("Duplicates per class:")
for cls in sorted(dupes_by_class.keys()):
    print(f"  {cls:30s}: {dupes_by_class[cls]}")

# ============================================================
# STEP 5: CROSS-CLASS DUPLICATES (MISLABELING CHECK)
# ============================================================
print("\n" + "=" * 70)
print("STEP 5: CROSS-CLASS DUPLICATES (MISLABELING)")
print("=" * 70)

print(f"Cross-class duplicate groups: {len(cross_class_dupes)}")

if cross_class_dupes:
    print("\n⚠️  WARNING: Same image appears in multiple classes!")
    print("    This indicates mislabeling or data leakage.")
    print("\nFirst 5 examples:")
    for h, paths in cross_class_dupes[:5]:
        print(f"\n  Hash: {h[:16]}...")
        for p in paths:
            cls = get_class_from_path(p, DATASET_DIR)
            print(f"    [{cls}] {p}")
else:
    print("✅ No cross-class duplicates found.")

# ============================================================
# STEP 6: SAVE REPORT
# ============================================================
print("\n" + "=" * 70)
print("STEP 6: SAVING REPORT")
print("=" * 70)

report_path = './duplicates_report.txt'
with open(report_path, 'w') as f:
    f.write("DUPLICATE IMAGES REPORT\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Dataset: {DATASET_DIR}\n")
    f.write(f"Total images: {len(all_images)}\n")
    f.write(f"Unique images: {len(hash_to_paths)}\n")
    f.write(f"Duplicate groups: {len(duplicates)}\n")
    f.write(f"Extra duplicate images: {total_extra}\n")
    f.write(f"Cross-class duplicate groups: {len(cross_class_dupes)}\n")
    f.write("\n" + "=" * 70 + "\n\n")
    
    f.write("PER-CLASS DUPLICATES\n")
    f.write("-" * 70 + "\n")
    for cls in sorted(dupes_by_class.keys()):
        f.write(f"  {cls}: {dupes_by_class[cls]}\n")
    f.write("\n" + "=" * 70 + "\n\n")
    
    f.write("ALL DUPLICATE GROUPS\n")
    f.write("-" * 70 + "\n")
    for h, paths in duplicates.items():
        classes = [get_class_from_path(p, DATASET_DIR) for p in paths]
        marker = " [CROSS-CLASS]" if len(set(classes)) > 1 else ""
        f.write(f"\nHash: {h}{marker}\n")
        for p in paths:
            cls = get_class_from_path(p, DATASET_DIR)
            f.write(f"  [{cls}] {p}\n")

print(f"Report saved: {report_path}")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
print(f"Total images:              {len(all_images)}")
print(f"Unique images:             {len(hash_to_paths)}")
print(f"Duplicate groups:          {len(duplicates)}")
print(f"Extra duplicate images:    {total_extra}")
print(f"Cross-class duplicates:    {len(cross_class_dupes)}")
print("=" * 70)

if len(duplicates) == 0:
    print("\n✅ DATASET IS CLEAN — No duplicates found.")
elif len(cross_class_dupes) > 0:
    print("\n❌ CROSS-CLASS DUPLICATES FOUND — Manual review required.")
else:
    print("\n⚠️  INTRA-CLASS DUPLICATES FOUND — Can be removed automatically.")