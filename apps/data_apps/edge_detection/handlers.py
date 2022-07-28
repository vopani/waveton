import os.path

from h2o_wave import Q, on

import cards
from actions import drop_cards, edge_detection_process
from constants import DROPPABLE_CARDS, DEFAULT_LOGGER, DEFAULT_EDGE_DETECTION_KERNEL_SIZE, DEFAULT_BLUR_KERNEL_SIZE, DEFAULT_EDGE_DETECTION_KERNEL
from initializers import initialize_client
from utils import apply_edge_detection


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
async def upload_image(q: Q):
    """
    Upload new image.
    """
    DEFAULT_LOGGER.info('Uploading new image')

    q.client.selected_image = q.args.image_uploader[0]

    # download image to local directory to process it using opencv
    q.client.selected_image_local_copy = await q.site.download(
        q.client.selected_image,
        os.path.join(q.app.images_dir, os.path.basename(q.client.selected_image))
    )

    q.client.edge_detection_kernel = DEFAULT_EDGE_DETECTION_KERNEL
    q.client.edge_detection_kernel_size = DEFAULT_EDGE_DETECTION_KERNEL_SIZE
    q.client.gaussian_kernel_size = DEFAULT_BLUR_KERNEL_SIZE

    await q.page.save()

    processed_image = apply_edge_detection(
        [q.client.selected_image_local_copy],
        processed_folder=q.app.processed_dir,
        edge_detection_kernel=q.client.edge_detection_kernel,
        edge_detection_kernel_size=q.client.edge_detection_kernel_size,
        smoothing=True,
        smoothing_kernel_size=q.client.gaussian_kernel_size
    )

    uploaded = await q.site.upload(
        processed_image
    )

    q.client.selected_processed_image = uploaded[0]

    q.page['commands_panel'] = cards.command_panel(
        edge_detection_kernel=q.client.edge_detection_kernel,
        edge_detection_kernel_size=q.client.edge_detection_kernel_size,
        gaussian_kernel_size=q.client.gaussian_kernel_size
    )

    q.page['original_image_viewer'] = cards.original_image_viewer(q.client.selected_image)
    q.page['processed_image_viewer'] = cards.processed_image_viewer(q.client.selected_processed_image)
    q.page['image_downloader'] = cards.image_downloader(q.client.selected_processed_image)

    await q.page.save()


@on()
async def edge_detection_kernel(q: Q):
    """
    Detect changes in edge detection configuration and apply them.
    """
    if q.args.upload_image and q.args.image_uploader:
        await upload_image(q)
    elif q.client.edge_detection_kernel != q.args.edge_detection_kernel or q.client.edge_detection_kernel_size != q.args.edge_detection_kernel_size or q.client.gaussian_kernel_size != q.args.gaussian_kernel_size:
        DEFAULT_LOGGER.info("Detected change in edge detection settings")
        await edge_detection_process(q)
    else:
        await q.page.save()
