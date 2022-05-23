import os.path

from h2o_wave import Q, on

import cards
from actions import drop_cards
from constants import DROPPABLE_CARDS, DEFAULT_LOGGER
from initializers import initialize_client
from utils import update_image_df, apply_edge_detection


@on('restart')
async def restart(q: Q):
    """
    Restart app.
    """

    DEFAULT_LOGGER.info('Restarting app')

    await drop_cards(q, DROPPABLE_CARDS)

    q.client.client_initialized = False
    await initialize_client(q)


@on('report')
async def report(q: Q):
    """
    Report error details.
    """

    DEFAULT_LOGGER.info('Displaying error details')

    q.page['error'].items[4].separator.visible = True
    q.page['error'].items[5].text.visible = True
    q.page['error'].items[6].text_l.visible = True
    q.page['error'].items[7].text.visible = True
    q.page['error'].items[8].text.visible = True
    q.page['error'].items[9].text.visible = True
    q.page['error'].items[10].text.visible = True
    q.page['error'].items[11].text.visible = True
    q.page['error'].items[12].text.visible = True

    await q.page.save()


@on()
async def image_uploader(q: Q):
    """
    Upload new image.
    """
    DEFAULT_LOGGER.info('Uploading new image')

    q.app.image_df = update_image_df(q.app.image_df, q.args.image_uploader[0])
    q.page['image_table'] = cards.image_table(q.app.image_df)
    await q.page.save()


@on()
async def image_table(q: Q):
    """
    Load selected image to image viewers.
    """
    DEFAULT_LOGGER.info(f'Loading {q.args.image_table[0]} to image viewer')

    q.client.selected_image = q.args.image_table[0]
    q.client.selected_processed_image = None

    # download image to local directory to process it using opencv
    q.client.selected_image_local_copy = await q.site.download(
        q.args.image_table[0],
        os.path.join(q.app.images_dir, os.path.basename(q.args.image_table[0]))
    )

    q.page['original_image_viewer'] = cards.original_image_viewer(q.client.selected_image)
    q.page['processed_image_viewer'] = cards.processed_image_viewer(q.client.selected_processed_image)

    await q.page.save()


@on()
async def run_edge_detection(q: Q):
    """
    Apply edge detection on selected image.
    """
    DEFAULT_LOGGER.info("Applying edge detection")

    if q.args.edge_detection_kernel:
        q.client.edge_detection_kernel = q.args.edge_detection_kernel

    if q.args.gaussian_blur:
        q.client.gaussian_blur = q.args.gaussian_blur

    if q.args.gaussian_kernel_size:
        q.client.gaussian_kernel_size = q.args.gaussian_kernel_size

    print(q.client.selected_image_local_copy)
    processed_image = apply_edge_detection(
        [q.client.selected_image_local_copy],
        processed_folder=q.app.processed_dir,
        edge_detection_kernel=q.client.edge_detection_kernel,
        smoothing=q.client.gaussian_blur,
        smoothing_kernel_size=q.client.gaussian_kernel_size
    )

    uploaded = await q.site.upload(
        processed_image
    )

    q.client.selected_processed_image = uploaded[0]

    q.app.image_df.loc[
        q.app.image_df.Image == q.client.selected_image, "Processed_Image"
    ] = q.client.selected_processed_image

    q.page['processed_image_viewer'] = cards.processed_image_viewer(q.client.selected_processed_image)
    await q.page.save()
