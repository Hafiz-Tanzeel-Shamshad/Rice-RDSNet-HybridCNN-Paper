from PIL import Image
import os

DATASET_DIR = './dataset'

corrupt_images = []
total_checked = 0

for cls in os.listdir(DATASET_DIR):
    cls_path = os.path.join(DATASET_DIR, cls)
    if not os.path.isdir(cls_path):
        continue
    
    for f in os.listdir(cls_path):
        if not f.lower().endswith(('.jpg','.jpeg','.png','.jfif')):
            continue
        
        path = os.path.join(cls_path, f)
        total_checked += 1
        try:
            img = Image.open(path)
            img.verify()
        except Exception as e:
            corrupt_images.append((path, str(e)))

print("=" * 70)
print("CORRUPT IMAGE CHECK")
print("=" * 70)
print(f"Total images checked: {total_checked}")
print(f"Corrupt images found: {len(corrupt_images)}")
if corrupt_images:
    print("\nCorrupt images:")
    for path, err in corrupt_images[:10]:
        print(f"  {path}")
        print(f"    Error: {err}")
print("=" * 70)