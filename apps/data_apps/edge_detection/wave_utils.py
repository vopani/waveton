import os
import glob

from h2o_wave import Q

from utils import apply_edge_detection
from constants import EdgeDetectionKernels


async def load_sample_images(q: Q):
    """
    Load sample lena image.
    """
    # grep all jpeg & png files under images directory
    image_paths = glob.glob(os.path.join(q.app.images_dir, "lena.png"))

    # apply edge_detection to sample
    apply_edge_detection(
        image_paths,
        processed_folder=q.app.processed_dir,
        edge_detection_kernel=EdgeDetectionKernels.SOBEL.value,
        edge_detection_kernel_size=3,
        smoothing=True,
        smoothing_kernel_size=3
    )

    # grep all processed samples
    processed_image_paths = glob.glob(os.path.join(q.app.processed_dir, "lena.png"))

    # load images
    sample_images = await q.site.upload(image_paths)
    processed_images = await q.site.upload(processed_image_paths)

    return sample_images[0], processed_images[0]
