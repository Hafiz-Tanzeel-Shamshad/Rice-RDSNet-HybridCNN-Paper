import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import os
import random
from tensorflow.keras.preprocessing import image

# ============================================================
# Step 1: Test set se random image picker
# ============================================================
def find_class_folder(base_dir, cname):
    """Case-insensitive + fuzzy folder matching."""
    if not os.path.isdir(base_dir):
        return None
    folders = [f for f in os.listdir(base_dir)
               if os.path.isdir(os.path.join(base_dir, f))]
    cname_norm = cname.lower().replace('_', ' ').replace('-', ' ')

    # 1. Exact match
    if cname in folders:
        return cname
    # 2. Case-insensitive exact
    for f in folders:
        if f.lower() == cname.lower():
            return f
    # 3. Fuzzy / partial
    for f in folders:
        f_norm = f.lower().replace('_', ' ').replace('-', ' ')
        if cname_norm in f_norm or f_norm in cname_norm:
            return f
    return None


def get_random_samples(test_dir, class_names, n_per_class=1, seed=None):
    """
    Randomly pick n_per_class images per class from TEST set.
    seed=None → different every run
    seed=42   → reproducible
    """
    if seed is not None:
        random.seed(seed)

    samples = {}
    for cname in class_names:
        folder = find_class_folder(test_dir, cname)
        if folder is None:
            print(f"⚠️  '{cname}' → folder not found in test set")
            continue
        cdir = os.path.join(test_dir, folder)
        files = [f for f in os.listdir(cdir)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif', '.bmp'))]
        if not files:
            print(f"⚠️  '{cname}' → folder empty")
            continue
        # ---- RANDOM PICK ----
        chosen = random.choice(files)
        samples[cname] = os.path.join(cdir, chosen)
        print(f"  🎲 {cname:28s} → {chosen}")
    return samples


# ============================================================
# Step 2: TEST_DIR set karein (agar pehle se nahi hai)
# ============================================================
# Option A: Agar aapke paas TEST_DIR variable already hai, skip karein
# Option B: Agar nahi hai, to yahan set karein:
# TEST_DIR = "/content/drive/MyDrive/rice_leaf_split/test"
# TEST_DIR = "/content/rice_dataset/RiceLeafDisease12classes/test"

print("Using TEST_DIR:", TEST_DIR)
print("Exists:", os.path.isdir(TEST_DIR))
print()

# ============================================================
# Step 3: Random samples pick karein
# ============================================================
# ----- CHANGE seed=None FOR RANDOM, seed=42 FOR REPRODUCIBLE -----
samples = get_random_samples(TEST_DIR, class_names, seed=None)

print(f"\n✅ Found samples for {len(samples)} classes\n")

# ============================================================
# Step 4: Display ke liye classes chunein (4 disease classes)
# ============================================================
preferred = ['brown_spot', 'leaf_blast', 'hispa', 'tungro']
display_classes = [c for c in preferred if c in samples]

# Fallback: agar koi missing ho to list bhar dein
if len(display_classes) < 4:
    print("⚠️  Filling from other available classes...")
    for c in samples:
        if c not in display_classes:
            display_classes.append(c)
        if len(display_classes) == 4:
            break

print(f"📊 Displaying {len(display_classes)} classes: {display_classes}\n")

# ============================================================
# Step 5: Last conv layer (Grad-CAM ke liye)
# ============================================================
last_conv = [l.name for l in best_model.layers if 'conv2d' in l.name][-1]
print(f"🔍 Using last conv layer: {last_conv}\n")

# ============================================================
# Step 6: Grad-CAM + Grid
# ============================================================
pretty_labels = {
    'brown_spot':            'Brown Spot',
    'leaf_blast':            'Leaf Blast',
    'hispa':                 'Hispa',
    'healthy_leaf':          'Healthy',
    'tungro':                'Tungro',
    'bacterial_leaf_blight': 'Bacterial Leaf Blight',
    'leaf_scald':            'Leaf Scald',
    'narrow_brown_spot':     'Narrow Brown Spot',
    'ragged_stunt_virus':    'Ragged Stunt Virus',
    'sheath_rot':            'Sheath Rot',
    'stem_rot':              'Stem Rot',
    'non_leaf':              'Non-Leaf',
}

n = len(display_classes)
fig, axes = plt.subplots(n, 3, figsize=(9, 2.8 * n))
if n == 1:
    axes = axes[np.newaxis, :]

for i, cname in enumerate(display_classes):
    img_path = samples[cname]
    img = image.load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))
    arr = image.img_to_array(img) / 255.0
    arr_batch = np.expand_dims(arr, axis=0)

    # Predict
    preds = best_model.predict(arr_batch, verbose=0)[0]
    pred_idx = int(np.argmax(preds))
    pred_class = class_names[pred_idx]
    conf = preds[pred_idx] * 100

    # Grad-CAM
    heatmap = make_gradcam_heatmap(arr_batch, best_model, last_conv,
                                   pred_index=pred_idx)
    heatmap_resized = tf.image.resize(heatmap[..., np.newaxis],
                                      (IMG_SIZE, IMG_SIZE)).numpy().squeeze()

    # Overlay
    jet = plt.cm.jet(heatmap_resized)[..., :3]
    overlay = np.clip(0.5 * arr + 0.5 * jet, 0, 1)

    label = pretty_labels.get(cname, cname)
    is_correct = (pred_class == cname)
    tick = "✅" if is_correct else "❌"

    axes[i, 0].imshow(img)
    axes[i, 0].set_title(f"True: {label}", fontsize=10, fontweight='bold')

    axes[i, 1].imshow(heatmap_resized, cmap='jet')
    axes[i, 1].set_title("Grad-CAM", fontsize=10)

    axes[i, 2].imshow(overlay)
    axes[i, 2].set_title(f"Pred: {pretty_labels.get(pred_class, pred_class)} "
                         f"({conf:.1f}%) {tick}", fontsize=10)

    for j in range(3):
        axes[i, j].axis('off')

plt.tight_layout()

# Save
out_path = os.path.join(SAVE_DIR, "gradcam_test_random.png")
plt.savefig(out_path, dpi=200, bbox_inches='tight')
plt.show()
print(f"\n💾 Saved: {out_path}")