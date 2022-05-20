import os
import pandas as pd

from h2o_wave import Q

from constants import DEFAULT_LOGGER
from actions import setup_home, update_theme
from wave_utils import load_sample_images


async def initialize_app(q: Q):
    """
    Initializing app.
    """
    if q.app.app_initialized:
        return

    DEFAULT_LOGGER.info('Initializing app')

    # initialize images dir
    q.app.images_dir = os.path.abspath("./images")
    os.makedirs(q.app.images_dir, exist_ok=True)

    # dataframe for image records
    q.app.image_df = await load_sample_images(q)

    q.app.app_initialized = True


async def initialize_client(q: Q):
    """
    Initializing client.
    """
    if q.client.client_initialized:
        # set theme
        if q.args.theme_dark is not None and q.args.theme_dark != q.client.theme_dark:
            await update_theme(q)
        return

    DEFAULT_LOGGER.info('Initializing client')

    q.client.theme_dark = True

    q.client.client_initialized = True

    await setup_home(q)
    await q.page.save()
