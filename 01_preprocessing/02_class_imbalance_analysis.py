import os

DATASET_DIR = './dataset'

classes = sorted([f for f in os.listdir(DATASET_DIR)
                  if os.path.isdir(os.path.join(DATASET_DIR, f))])

counts = {}
for cls in classes:
    cls_path = os.path.join(DATASET_DIR, cls)
    images = [f for f in os.listdir(cls_path)
              if f.lower().endswith(('.jpg','.jpeg','.png','.jfif'))]
    counts[cls] = len(images)

max_count = max(counts.values())
min_count = min(counts.values())

print("=" * 70)
print("CLASS IMBALANCE ANALYSIS")
print("=" * 70)
print(f"Max class size: {max_count} ({max(counts, key=counts.get)})")
print(f"Min class size: {min_count} ({min(counts, key=counts.get)})")
print(f"Imbalance ratio: {max_count / min_count:.2f}:1")
print("=" * 70)

if max_count / min_count > 5:
    print("⚠️  Heavy imbalance detected.")
elif max_count / min_count > 2:
    print("⚠️  Moderate imbalance detected.")
else:
    print("✅ Dataset is relatively balanced.")