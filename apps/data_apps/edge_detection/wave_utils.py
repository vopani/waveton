import os
import glob
from datetime import datetime
import pandas as pd

from h2o_wave import Q

from utils import apply_edge_detection


async def load_sample_images(q: Q):
    # grep all jpeg & png files under images directory
    image_paths = glob.glob(os.path.join(q.app.images_dir, "*.jpeg"))
    image_paths.extend(glob.glob(os.path.join(q.app.images_dir, "*.png")))

    # apply edge_detection to sample
    apply_edge_detection(image_paths, processed_folder=q.app.processed_dir)

    # grep all processed samples
    processed_image_paths = glob.glob(os.path.join(q.app.processed_dir, "*"))

    # load images
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sample_images = await q.site.upload(image_paths)
    processed_images = await q.site.upload(processed_image_paths)

    return pd.DataFrame({
        "Image": sample_images,
        "Processed_Image": processed_images,
        "Timestamp": [timestamp] * len(sample_images)
    })
