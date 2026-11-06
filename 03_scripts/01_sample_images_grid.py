import os
import matplotlib.pyplot as plt
from PIL import Image

BASE = "./rice_leaf_disease_dataset"
classes = sorted(os.listdir(os.path.join(BASE, "train")))
extensions = (".jpg", ".jpeg", ".png", ".jfif", ".webp")

fig, axes = plt.subplots(3, 4, figsize=(16, 12))
axes = axes.flatten()

for i, cls in enumerate(classes[:12]):
    cls_path = os.path.join(BASE, "train", cls)
    images = [f for f in os.listdir(cls_path) if f.lower().endswith(extensions)]
    if images:
        img_path = os.path.join(cls_path, images[0])
        img = Image.open(img_path)
        axes[i].imshow(img)
        axes[i].set_title(cls, fontsize=10)
        axes[i].axis('off')

plt.suptitle('Sample Images per Class (Training Set)', fontsize=14)
plt.tight_layout()
plt.savefig('sample_images.png', dpi=300)
plt.show()