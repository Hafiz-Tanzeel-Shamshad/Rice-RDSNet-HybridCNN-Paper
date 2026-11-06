import os
import hashlib
import shutil
from collections import defaultdict

DATASET_DIR = './dataset'
BACKUP_DIR = './dataset_duplicates_backup'  # deleted images yahan jayengi

def md5_hash(filepath):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def get_all_images(folder):
    images = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(('.jpg','.jpeg','.png','.jfif','.webp')):
                images.append(os.path.join(root, f))
    return images

# Sab images
all_images = get_all_images(DATASET_DIR)
print(f"Total images: {len(all_images)}")

# Hash map
hash_to_paths = defaultdict(list)
for path in all_images:
    try:
        h = md5_hash(path)
        hash_to_paths[h].append(path)
    except Exception as e:
        print(f"Error: {path} → {e}")

# Duplicates dhoondein aur backup mein move karein
os.makedirs(BACKUP_DIR, exist_ok=True)
removed = 0

for h, paths in hash_to_paths.items():
    if len(paths) > 1:
        # Pehli rakhne do, baqi backup mein bhejo
        for path in paths[1:]:
            rel = os.path.relpath(path, DATASET_DIR)
            backup_path = os.path.join(BACKUP_DIR, rel)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.move(path, backup_path)
            removed += 1

print(f"\nRemoved {removed} duplicate images.")
print(f"Backup saved to: {BACKUP_DIR}")
print(f"Remaining unique images: {len(all_images) - removed}")