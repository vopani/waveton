import logging
from pathlib import Path

from h2o_wave import Q, main, app, copy_expando, handle_on, on

import cards

# Set up logging
logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)


@app('/')
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """

    try:
        # Initialize the app if not already
        if not q.app.initialized:
            await initialize_app(q)

        # Initialize the client if not already
        if not q.client.initialized:
            await initialize_client(q)

        # Update theme if toggled
        elif q.args.theme_dark is not None and q.args.theme_dark != q.client.theme_dark:
            await update_theme(q)

        # Update tab if switched
        elif q.args.tab is not None and q.args.tab != q.client.tab:
            await update_tab(q)

        # Delegate query to query handlers
        elif await handle_on(q):
            pass

        # Adding this condition to help in identifying bugs
        else:
            await handle_fallback(q)

    except Exception as error:
        await show_error(q, error=str(error))


async def initialize_app(q: Q):
    """
    Initialize the app.
    """
    logging.info('Initializing app')

    # Set initial argument values
    q.app.cards = ['upload', 'table', 'error']

    # Upload default image
    q.app.path_default_image, = await q.site.upload(files=['sample.jpeg'])

    q.app.initialized = True


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """
    logging.info('Initializing client')

    # Set initial argument values
    q.client.theme_dark = True
    q.client.tab = 'light'

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for the main page
    q.page['augmentations'] = cards.augmentations(
        tab=q.client.tab
    )
    q.page['images'] = cards.images()

    q.client.initialized = True

    await q.page.save()


async def update_theme(q: Q):
    """
    Update theme of app.
    """
    # Copying argument values to client
    copy_expando(q.args, q.client)

    if q.client.theme_dark:
        logging.info('Updating theme to dark mode')

        # Update theme from light to dark mode
        q.page['meta'].theme = 'h2o-dark'
        q.page['header'].icon_color = 'black'
    else:
        logging.info('Updating theme to light mode')

        # Update theme from dark to light mode
        q.page['meta'].theme = 'light'
        q.page['header'].icon_color = '#FEC924'

    await q.page.save()


async def update_tab(q: Q):
    """
    Update tab of augmentations.
    """
    # Copying argument values to client
    copy_expando(q.args, q.client)

    if q.client.tab == 'heavy':
        logging.info('Updating tab from light to heavy')
    else:
        logging.info('Updating tab from heavy to light')

    # Update list of augmentations
    q.page['augmentations'] = cards.augmentations(
        tab=q.client.tab
    )

    await q.page.save()


@on('upload')
async def update_data(q: Q):
    """
    Update data from csv file.
    """

    logging.info('Updating data from csv file')

    # Download data
    path_data = await q.site.download(q.args.upload[0], '.')
    data = dt.fread(path_data)
    name = Path(path_data).name

    # Update table with data
    q.page['upload'] = cards.upload(path_default_data=q.app.path_default_data)
    q.page['table'] = cards.table(name=name, data=data)

    await q.page.save()


def clear_cards(q: Q, card_names: list):
    """
    Clear cards from the page.
    """

    logging.info('Clearing cards')

    # Delete cards from the page
    for card_name in card_names:
        del q.page[card_name]


async def show_error(q: Q, error: str):
    """
    Displays errors.
    """

    logging.error(error)

    # Clear all cards
    clear_cards(q, q.app.cards)

    # Format and display the error
    q.page['error'] = cards.crash_report(q)

    await q.page.save()


@on('reload')
async def reload_client(q: Q):
    """
    Reset the client.
    """

    logging.info('Reloading client')

    # Clear all cards
    clear_cards(q, q.app.cards)

    # Reload the client
    await initialize_client(q)


async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    """

    logging.info('Adding fallback page')

    q.page['fallback'] = cards.fallback

    await q.page.save()