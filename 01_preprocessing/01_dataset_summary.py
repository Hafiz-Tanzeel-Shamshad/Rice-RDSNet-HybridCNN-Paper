import os

DATASET_DIR = './rice_leaf_disease_dataset'

# Saari classes (folders) list karein
classes = sorted([f for f in os.listdir(DATASET_DIR) 
                  if os.path.isdir(os.path.join(DATASET_DIR, f))])

print("=" * 70)
print("DATASET SUMMARY")
print("=" * 70)
print(f"Total classes: {len(classes)}")
print("-" * 70)

total_images = 0
class_counts = {}

for cls in classes:
    cls_path = os.path.join(DATASET_DIR, cls)
    images = [f for f in os.listdir(cls_path)
              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif', '.JPG', '.JPEG', '.PNG'))]
    count = len(images)
    total_images += count
    class_counts[cls] = count
    print(f"{cls:30s} : {count:5d} images")

print("-" * 70)
print(f"{'TOTAL':30s} : {total_images:5d} images")
print("=" * 70)