from h2o_wave import Q

import cards
from constants import DEFAULT_LOGGER, DROPPABLE_CARDS


async def setup_home(q: Q):
    """
    Set up home page of app.
    """
    q.page['meta'] = cards.meta()
    q.page['header'] = cards.header()
    q.page['commands_panel'] = cards.command_panel(
        edge_detection_kernel=q.client.edge_detection_kernel,
        gaussian_blur=q.client.gaussian_blur,
        gaussian_kernel_size=q.client.gaussian_kernel_size
    )
    q.page['original_image_viewer'] = cards.original_image_viewer(q.client.selected_image)
    q.page['processed_image_viewer'] = cards.processed_image_viewer(q.client.selected_processed_image)
    q.page['image_table'] = cards.image_table(q.app.image_df)
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

