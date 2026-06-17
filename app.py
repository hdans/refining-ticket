import streamlit as st
import numpy as np
from PIL import Image
from skimage.exposure import match_histograms
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import io
import os
from datetime import datetime
from pathlib import Path

DATASET_DIRS = ["train", "test"]
VALIDATION_DIR = "validation"
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

MAX_DISPLAY_WIDTH = 1600


def collect_validation_images():
    folder = Path(VALIDATION_DIR)
    if not folder.exists():
        return {}
    images = {}
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
        for f in sorted(folder.glob(ext)):
            images[f.name] = f
    return images


def collect_dataset_images():
    images = {}
    for folder in DATASET_DIRS:
        folder_path = Path(folder)
        if not folder_path.exists():
            continue
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
            for f in sorted(folder_path.glob(ext)):
                images[f"{folder}/{f.name}"] = f
    return images


def load_image(source) -> np.ndarray:
    if isinstance(source, (str, Path)):
        img = Image.open(source).convert("RGB")
    else:
        img = Image.open(source).convert("RGB")
    return np.array(img)


def maybe_resize(img_array: np.ndarray, max_width: int = MAX_DISPLAY_WIDTH) -> np.ndarray:
    h, w = img_array.shape[:2]
    if w > max_width:
        scale = max_width / w
        new_w = max_width
        new_h = int(h * scale)
        pil_img = Image.fromarray(img_array).resize((new_w, new_h), Image.LANCZOS)
        return np.array(pil_img)
    return img_array


def apply_histogram_matching(source: np.ndarray, reference: np.ndarray) -> np.ndarray:
    matched = match_histograms(source, reference, channel_axis=-1)
    return matched.astype(np.uint8)


def plot_histograms(source: np.ndarray, reference: np.ndarray, result: np.ndarray):
    fig, axes = plt.subplots(3, 3, figsize=(12, 7))
    channel_colors = ["red", "green", "blue"]
    channel_names = ["R", "G", "B"]
    row_labels = ["Original", "Reference", "Result"]
    images = [source, reference, result]

    for row, (img, label) in enumerate(zip(images, row_labels)):
        for col, (color, ch_name) in enumerate(zip(channel_colors, channel_names)):
            ax = axes[row][col]
            ax.hist(img[:, :, col].ravel(), bins=256, range=(0, 256), color=color, alpha=0.75, density=True)
            if row == 0:
                ax.set_title(f"Channel {ch_name}", fontsize=10)
            if col == 0:
                ax.set_ylabel(label, fontsize=10)
            ax.set_xlim(0, 255)
            ax.tick_params(labelsize=7)

    plt.suptitle("Histogram per Channel (R / G / B)", fontsize=12, y=1.01)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def image_to_bytes(img_array: np.ndarray, fmt: str = "PNG") -> bytes:
    pil_img = Image.fromarray(img_array)
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    return buf.getvalue()


def save_output(result: np.ndarray, original_name: str) -> Path:
    stem = Path(original_name).stem if original_name else "result"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUTS_DIR / f"{stem}_matched_{timestamp}.png"
    Image.fromarray(result).save(output_path)
    return output_path


def main():
    st.set_page_config(
        page_title="Histogram Matching — Receipt Image",
        page_icon="🧾",
        layout="wide",
    )

    st.title("🧾 Histogram Matching on Receipt / Ticket Images")
    st.markdown(
        "Upload a receipt or ticket image. The app will apply **Histogram Matching** "
        "using a reference image from the dataset to normalize color, brightness, and contrast."
    )

    dataset_images = collect_dataset_images()

    if not dataset_images:
        st.error("No dataset images found. Make sure the `train/` or `test/` folder exists with images.")
        return

    st.sidebar.header("Reference Image")

    ref_mode = st.sidebar.radio(
        "Reference mode",
        ["Use default reference", "Choose from dataset"],
        index=0,
    )

    default_ref_key = list(dataset_images.keys())[0]

    if ref_mode == "Choose from dataset":
        selected_ref_key = st.sidebar.selectbox(
            "Pick a reference image",
            options=list(dataset_images.keys()),
            index=0,
        )
    else:
        selected_ref_key = default_ref_key

    ref_path = dataset_images[selected_ref_key]

    st.sidebar.markdown("---")
    st.sidebar.header("Preprocessing Options")

    resize_input = st.sidebar.checkbox("Resize large input image", value=True)
    show_histograms = st.sidebar.checkbox("Show histogram comparison", value=True)

    st.sidebar.markdown("---")
    val_images = collect_validation_images()
    st.sidebar.caption(
        f"Dataset: {len(dataset_images)} images ({', '.join(DATASET_DIRS)})  \n"
        f"Validation: {len(val_images)} degraded images"
    )

    tab_upload, tab_validation = st.tabs(["Upload Image", "Use Validation Image"])

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload your receipt / ticket image",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, JPEG, PNG",
        )

    with tab_validation:
        if val_images:
            val_cols = st.columns([2, 1])
            with val_cols[0]:
                selected_val = st.selectbox(
                    "Pick a degraded validation image",
                    options=list(val_images.keys()),
                    format_func=lambda n: n,
                )
            with val_cols[1]:
                st.markdown("**Degradation types included:**")
                st.markdown(
                    "- `dark` — brightness ×0.35\n"
                    "- `very_dark` — brightness ×0.18\n"
                    "- `overexposed` — brightness ×1.55\n"
                    "- `low_contrast` — compressed range\n"
                    "- `warm_tint` — red boosted, blue cut\n"
                    "- `cool_tint` — blue boosted, red cut\n"
                    "- `noisy_dark` — dark + Gaussian noise\n"
                    "- `faded` — washed-out midtones"
                )
            use_val = st.button("Load this validation image", type="primary")
        else:
            st.warning("No validation images found. Run `python make_validation.py` to generate them.")
            use_val = False
            selected_val = None

    source_path_override = None
    if "val_images" not in st.session_state:
        st.session_state["val_images"] = {}
    if val_images:
        st.session_state["val_images"] = val_images

    if use_val and selected_val:
        st.session_state["active_val"] = selected_val

    active_val = st.session_state.get("active_val")

    if active_val and active_val in st.session_state.get("val_images", {}):
        source_path_override = st.session_state["val_images"][active_val]
        uploaded_file = None

    if uploaded_file is None and source_path_override is None:
        st.info("Upload an image above or pick a validation image to get started.")
        st.subheader("Selected Reference Image Preview")
        ref_preview = load_image(ref_path)
        st.image(ref_preview, caption=f"Reference: {selected_ref_key}", use_container_width=False, width=400)
        return

    if source_path_override is not None:
        source_arr = load_image(source_path_override)
        display_name = source_path_override.name
    else:
        source_arr = load_image(uploaded_file)
        display_name = uploaded_file.name
    if resize_input:
        source_arr = maybe_resize(source_arr)

    ref_arr = load_image(ref_path)

    result_arr = apply_histogram_matching(source_arr, ref_arr)

    output_path = save_output(result_arr, display_name)

    st.subheader("Results")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Original (Input)**")
        st.image(source_arr, use_container_width=True)
        st.caption(f"{display_name}  |  {source_arr.shape[1]}×{source_arr.shape[0]} px")

    with col2:
        st.markdown("**Reference Image**")
        st.image(ref_arr, use_container_width=True)
        st.caption(f"{selected_ref_key}  |  {ref_arr.shape[1]}×{ref_arr.shape[0]} px")

    with col3:
        st.markdown("**Histogram Matching Result**")
        st.image(result_arr, use_container_width=True)
        st.caption(f"Saved → {output_path}")

    st.markdown("---")

    result_bytes = image_to_bytes(result_arr)
    st.download_button(
        label="⬇️  Download Result Image",
        data=result_bytes,
        file_name=output_path.name,
        mime="image/png",
        use_container_width=False,
    )

    if show_histograms:
        st.subheader("Histogram Comparison")
        hist_buf = plot_histograms(source_arr, ref_arr, result_arr)
        st.image(hist_buf, use_container_width=True)


if __name__ == "__main__":
    main()
