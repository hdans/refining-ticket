from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np
import random

random.seed(42)
np.random.seed(42)

source_images = random.sample(list(Path("test").glob("*.jpg")), 20)

out_dir = Path("validation")
out_dir.mkdir(exist_ok=True)

degradation_map = {
    0:  "dark",
    1:  "dark",
    2:  "dark",
    3:  "dark",
    4:  "overexposed",
    5:  "overexposed",
    6:  "low_contrast",
    7:  "low_contrast",
    8:  "low_contrast",
    9:  "warm_tint",
    10: "warm_tint",
    11: "cool_tint",
    12: "cool_tint",
    13: "noisy_dark",
    14: "noisy_dark",
    15: "faded",
    16: "faded",
    17: "very_dark",
    18: "very_dark",
    19: "very_dark",
}


def apply_dark(img):
    return ImageEnhance.Brightness(img).enhance(0.35)


def apply_very_dark(img):
    return ImageEnhance.Brightness(img).enhance(0.18)


def apply_overexposed(img):
    arr = np.clip(np.array(ImageEnhance.Brightness(img).enhance(1.55)), 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def apply_low_contrast(img):
    arr = np.array(img).astype(np.float32)
    arr = arr * 0.45 + 100
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def apply_warm_tint(img):
    arr = np.array(ImageEnhance.Brightness(img).enhance(0.35)).astype(np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.35, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.65, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def apply_cool_tint(img):
    arr = np.array(ImageEnhance.Brightness(img).enhance(0.35)).astype(np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 0.65, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 1.35, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def apply_noisy_dark(img):
    arr = np.array(ImageEnhance.Brightness(img).enhance(0.30)).astype(np.float32)
    noise = np.random.normal(0, 12, arr.shape)
    return Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8))


def apply_faded(img):
    arr = np.array(img).astype(np.float32)
    arr = arr * 0.55 + 90
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


apply_fn = {
    "dark":         apply_dark,
    "very_dark":    apply_very_dark,
    "overexposed":  apply_overexposed,
    "low_contrast": apply_low_contrast,
    "warm_tint":    apply_warm_tint,
    "cool_tint":    apply_cool_tint,
    "noisy_dark":   apply_noisy_dark,
    "faded":        apply_faded,
}

created = []
for idx, src_path in enumerate(source_images):
    deg_type = degradation_map[idx]
    img = Image.open(src_path).convert("RGB")
    result = apply_fn[deg_type](img)
    out_name = f"{src_path.stem}_{deg_type}.jpg"
    out_path = out_dir / out_name
    result.save(out_path, quality=92)
    created.append((out_name, deg_type, np.array(result).mean()))

print(f"Created {len(created)} validation images in validation/\n")
header = f"{'Filename':<52} {'Type':<15} {'Mean brightness':>16}"
print(header)
print("-" * len(header))
for name, deg, mean in created:
    print(f"{name:<52} {deg:<15} {mean:>16.1f}")
