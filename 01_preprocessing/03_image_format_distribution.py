import os
from collections import Counter

DATASET_DIR = './dataset'

extensions = []
for cls in os.listdir(DATASET_DIR):
    cls_path = os.path.join(DATASET_DIR, cls)
    if os.path.isdir(cls_path):
        for f in os.listdir(cls_path):
            ext = os.path.splitext(f)[1].lower()
            if ext:
                extensions.append(ext)

print("=" * 70)
print("IMAGE FORMAT DISTRIBUTION")
print("=" * 70)
for ext, count in Counter(extensions).most_common():
    print(f"  {ext}: {count}")
print("=" * 70)