import os
import glob
from datetime import datetime
import pandas as pd

from h2o_wave import Q


async def load_sample_images(q: Q):
    # grep all jpeg & png files under images directory
    image_paths = glob.glob(os.path.join(q.app.images_dir, "*.jpeg"))
    image_paths.extend(glob.glob(os.path.join(q.app.images_dir, "*.png")))

    # load images
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sample_images = await q.site.upload(image_paths)

    return pd.DataFrame({
        "Image": sample_images,
        "Timestamp": [timestamp] * len(sample_images)
    })
