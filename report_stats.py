from pathlib import Path
from PIL import Image
from skimage.exposure import match_histograms
import numpy as np

val = list(Path("validation").glob("*.jpg"))
ref_path = list(Path("train").glob("*.jpg"))[0]
ref_arr = np.array(Image.open(ref_path).convert("RGB"))

print(f"Reference image : {ref_path.name}")
print(f"Reference mean  : {ref_arr.mean():.2f}")
print()

rows = []
for p in sorted(val):
    src = np.array(Image.open(p).convert("RGB"))
    matched = match_histograms(src, ref_arr, channel_axis=-1).astype(np.uint8)
    deg = "_".join(p.stem.split("_")[1:])
    diff_before = abs(src.mean() - ref_arr.mean())
    diff_after  = abs(matched.mean() - ref_arr.mean())
    rows.append((p.name, deg, src.mean(), matched.mean(), diff_before, diff_after))

header = f"{'Filename':<45} {'Type':<14} {'Src':>7} {'Result':>8} {'DiffBefore':>11} {'DiffAfter':>10}"
print(header)
print("-" * len(header))
for r in rows:
    print(f"{r[0]:<45} {r[1]:<14} {r[2]:>7.1f} {r[3]:>8.1f} {r[4]:>11.1f} {r[5]:>10.2f}")

avg_before = np.mean([r[4] for r in rows])
avg_after  = np.mean([r[5] for r in rows])
print()
print(f"Average brightness deviation before matching : {avg_before:.2f}")
print(f"Average brightness deviation after  matching : {avg_after:.2f}")
print(f"Reduction in deviation : {((avg_before - avg_after) / avg_before) * 100:.1f}%")
