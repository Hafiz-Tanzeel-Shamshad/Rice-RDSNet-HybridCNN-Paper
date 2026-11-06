import os
import matplotlib.pyplot as plt
import numpy as np

BASE = "./rice_leaf_disease_dataset"
extensions = (".jpg", ".jpeg", ".png", ".jfif", ".webp")

classes = sorted(os.listdir(os.path.join(BASE, "train")))

train_counts = []
val_counts = []
test_counts = []

for cls in classes:
    train_counts.append(len([f for f in os.listdir(os.path.join(BASE, "train", cls))
                             if f.lower().endswith(extensions)]))
    val_counts.append(len([f for f in os.listdir(os.path.join(BASE, "validation", cls))
                           if f.lower().endswith(extensions)]))
    test_counts.append(len([f for f in os.listdir(os.path.join(BASE, "test", cls))
                            if f.lower().endswith(extensions)]))

# Shorten class names for x-axis
short_names = [cls.replace('_', ' ').title() for cls in classes]

x = np.arange(len(classes))
width = 0.27

fig, ax = plt.subplots(figsize=(12, 5))

ax.bar(x - width, train_counts, width, label='Train', color='#2E86AB')
ax.bar(x, val_counts, width, label='Validation', color='#A23B72')
ax.bar(x + width, test_counts, width, label='Test', color='#F18F01')

ax.set_ylabel('Number of Images', fontsize=11)
ax.set_title('Class Distribution Across Training, Validation, and Test Splits', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(short_names, rotation=45, ha='right', fontsize=9)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('fig1_class_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

print("Saved: fig1_class_distribution.png")