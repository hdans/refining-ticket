# Histogram Matching on Receipt / Ticket Images

## Purpose

This app demonstrates **Histogram Matching** as an image preprocessing technique applied to receipt and ticket images. The goal is to normalize the color distribution of an uploaded image so it matches the tonal characteristics of a cleaner reference image from the dataset — improving consistency in brightness, contrast, and color balance before further processing.

## How Histogram Matching Works (Simple Explanation)

Every image has a histogram — a graph that shows how many pixels exist at each brightness level (0 = black, 255 = white) for each color channel (Red, Green, Blue).

Histogram matching takes the histogram of a **source image** and reshapes it so it looks like the histogram of a **reference image**. It does this by computing a mapping function: for each brightness value in the source, it finds the equivalent brightness value in the reference and substitutes it.

The result is an image that keeps the original content (shapes, text, objects) but has the same overall color and brightness distribution as the reference. This is useful when images in a dataset were taken under different lighting conditions or with different cameras.

## How to Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
streamlit run app.py
```

3. Open your browser at `http://localhost:8501`.

## Folder Structure

```
uas/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── outputs/             # Saved result images (auto-created)
├── train/               # Training dataset images (626 images)
└── test/                # Test dataset images (347 images)
```

## App Features

- Upload any receipt or ticket image (JPG, JPEG, PNG).
- Choose a reference image from the `train/` or `test/` dataset, or use the default (first image in the dataset).
- Side-by-side display of original, reference, and matched result.
- Optional histogram visualization comparing all three images across R, G, B channels.
- Download button for the result image.
- All results are automatically saved to the `outputs/` folder with a timestamp.

## Limitations

Histogram matching normalizes the **statistical distribution** of pixel intensities. It is not a general-purpose image enhancement tool. Specifically:

- It **cannot fix motion blur** or out-of-focus images. If the original image is blurry, the result will still be blurry.
- It **cannot recover damaged or missing text**. If text detail is lost due to poor scanning or damage, matching will not restore it.
- It **assumes the reference image is reasonably clean**. If the reference has poor quality, the result will inherit those characteristics.
- It may produce **color artifacts** if the source and reference images have very different content (e.g., one is mostly white paper, the other has dark backgrounds).
- It works best when source and reference images are of a **similar type** — in this case, both being receipts or tickets improves results.
"# refining-ticket" 
