from h2o_wave import Q

import cards
from constants import DEFAULT_LOGGER, DROPPABLE_CARDS
from utils import apply_edge_detection


async def setup_home(q: Q):
    """
    Set up home page of app.
    """
    q.page['meta'] = cards.meta()
    q.page['header'] = cards.header()
    q.page['commands_panel'] = cards.command_panel(
        edge_detection_kernel=q.client.edge_detection_kernel,
        edge_detection_kernel_size=q.client.edge_detection_kernel_size,
        gaussian_kernel_size=q.client.gaussian_kernel_size
    )
    q.page['original_image_viewer'] = cards.original_image_viewer(q.client.selected_image)
    q.page['processed_image_viewer'] = cards.processed_image_viewer(q.client.selected_processed_image)
    q.page['image_uploader'] = cards.image_uploader()
    q.page['image_downloader'] = cards.image_downloader(q.client.selected_processed_image)
    q.page['footer'] = cards.footer()

    await q.page.save()


async def update_theme(q: Q):
    """
    Update theme of app.
    """

    q.client.theme_dark = q.args.theme_dark

    if q.client.theme_dark:
        DEFAULT_LOGGER.info('Updating theme to dark mode')

        q.page['meta'].theme = 'h2o-dark'
        q.page['header'].icon_color = 'black'
    else:
        DEFAULT_LOGGER.info('Updating theme to light mode')

        q.page['meta'].theme = 'light'
        q.page['header'].icon_color = '#FEC924'

    q.page['header'].items[0].toggle.value = q.client.theme_dark

    await q.page.save()


async def drop_cards(q: Q, card_names: list):
    """
    Drop cards from Wave page.
    """

    DEFAULT_LOGGER.info('Clearing cards')

    for card_name in card_names:
        del q.page[card_name]


async def show_error(q: Q, error: str):
    """
    Displays errors.
    """

    DEFAULT_LOGGER.error(error)

    # Drop all cards from the page.
    await drop_cards(q, DROPPABLE_CARDS)

    # Format and display the error.
    q.page['error'] = cards.create_crash_report(q)

    await q.page.save()


async def edge_detection_process(q: Q):
    DEFAULT_LOGGER.info("Running edge detection process")

    if q.args.edge_detection_kernel:
        q.client.edge_detection_kernel = q.args.edge_detection_kernel

    if q.args.edge_detection_kernel_size:
        q.client.edge_detection_kernel_size = q.args.edge_detection_kernel_size

    if q.args.gaussian_kernel_size:
        q.client.gaussian_kernel_size = q.args.gaussian_kernel_size

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
    q.page['image_downloader'] = cards.image_downloader(q.client.selected_processed_image)
    q.page['processed_image_viewer'] = cards.processed_image_viewer(q.client.selected_processed_image)
    await q.page.save()
