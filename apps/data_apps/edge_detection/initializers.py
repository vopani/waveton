import os

from h2o_wave import Q

from constants import DEFAULT_LOGGER, DEFAULT_EDGE_DETECTION_KERNEL, DEFAULT_BLUR_KERNEL_SIZE, DEFAULT_EDGE_DETECTION_KERNEL_SIZE
from actions import setup_home, update_theme
from wave_utils import load_sample_images


async def initialize_app(q: Q):
    """
    Initializing the app.
    """
    if q.app.app_initialized:
        return

    DEFAULT_LOGGER.info('Initializing app')

    # initialize images dir
    q.app.images_dir = os.path.abspath("./images")
    q.app.processed_dir = os.path.abspath("./images/processed")
    os.makedirs(q.app.images_dir, exist_ok=True)
    os.makedirs(q.app.processed_dir, exist_ok=True)

    # # dataframe for image records
    q.app.sample_source_image, q.app.sample_processed_image = await load_sample_images(q)

    q.app.app_initialized = True


async def initialize_client(q: Q):
    """
    Initializing client (browser tab).
    """
    if q.client.client_initialized:
        if q.args.theme_dark is not None and q.args.theme_dark != q.client.theme_dark:
            await update_theme(q)
        return

    DEFAULT_LOGGER.info('Initializing client')

    q.client.theme_dark = True

    q.client.selected_image_local_copy = os.path.join(q.app.images_dir, "lena.png")
    q.client.selected_image = q.app.sample_source_image
    q.client.selected_processed_image = q.app.sample_processed_image

    q.client.edge_detection_kernel = DEFAULT_EDGE_DETECTION_KERNEL
    q.client.edge_detection_kernel_size = DEFAULT_EDGE_DETECTION_KERNEL_SIZE
    q.client.gaussian_kernel_size = DEFAULT_BLUR_KERNEL_SIZE

    q.client.client_initialized = True

    await setup_home(q)
    await q.page.save()

