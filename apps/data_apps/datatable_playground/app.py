import logging
from pathlib import Path
from uuid import uuid4

import datatable as dt
from h2o_wave import Q, main, app, copy_expando, handle_on, on

import cards
import utils

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

        # Update table if query is edited
        elif q.args.query is not None and q.args.query != q.client.query:
            await apply_query(q)

        # Update dataset if changed
        elif q.args.dataset is not None and q.args.dataset != q.client.dataset:
            await update_dataset(q)

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

    q.app.default_data = dt.fread('waveton_sample.csv')
    q.app.cards = ['main', 'error']

    q.app.initialized = True


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')

    # Set initial argument values
    q.client.theme_dark = True
    q.client.datasets = ['waveton_sample.csv']
    q.client.dataset = 'waveton_sample.csv'
    q.client.data = q.app.default_data
    q.client.data_query = q.client.data
    q.client.query = ''

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for the main page
    q.page['main'] = cards.main

    q.client.initialized = True

    await update_table(q)


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


async def update_table(q: Q):
    """
    Update table.
    """

    logging.info('Updating table')

    # Update query
    q.page['main'].items[1].separator.label = q.client.query

    # Update table name with random string
    q.page['main'].items[2].table.name = str(uuid4())

    # Update table columns
    q.page['main'].items[2].table.columns = utils.create_table_columns(data=q.client.data_query)

    # Update table rows
    q.page['main'].items[2].table.rows = utils.create_table_rows(data=q.client.data_query)

    await q.page.save()


async def update_dataset(q: Q):
    """
    Update dataset.
    """

    logging.info('Updating dataset')

    if q.args.dataset is not None:
        q.client.dataset = q.args.dataset

    # Update to new dataset
    q.client.data = dt.fread(q.client.dataset)
    q.client.data_query = q.client.data

    # Reset query
    q.client.query = ''

    # Update dropdown
    q.page['main'].items[0].inline.items[1].dropdown.choices = utils.create_choices_from_list(values=q.client.datasets)
    q.page['main'].items[0].inline.items[1].dropdown.value = q.client.dataset

    await update_table(q)


@on('add_dataset')
async def add_dataset(q: Q):
    """
    Add a new dataset.
    """

    logging.info('Adding a new dataset')

    q.page['meta'].dialog = cards.dialog_upload_dataset

    await q.page.save()


@on('upload')
async def upload_dataset(q: Q):
    """
    Upload dataset.
    """

    logging.info('Uploading new dataset')

    # Download dataset to app
    path_data = Path(await q.site.download(q.args.upload[0], '.'))

    # Update to new dataset
    q.client.dataset = path_data.name
    q.client.datasets.append(q.client.dataset)

    # Remove dialog
    q.page['meta'].dialog = None

    await update_dataset(q)


async def apply_query(q: Q):
    """
    Apply query on the data.
    """

    logging.info('Applying query')

    # Save query
    q.client.query = q.args.query

    # Update data based on query
    if q.client.query == '':
        # Reset data
        q.client.data_query = q.client.data

        await update_table(q)
    else:
        try:
            # Check if query is valid
            data_query = eval(utils.prepare_query(q.client.query))
            q.client.data_query = data_query

            await update_table(q)
        except:
            # Ignore any errors
            await handle_fallback(q)


@on('dialog_upload_dataset.dismissed')
async def dismiss_dialog(q: Q):
    """
    Dismiss dialog.
    """

    logging.info('Dismissing dialog')

    q.page['meta'].dialog = None

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
