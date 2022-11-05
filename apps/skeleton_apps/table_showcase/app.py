import logging

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

        # Update table if changed
        elif q.events.transactions:
            await update_table(q)

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
    q.app.cards = ['table', 'error']

    q.app.initialized = True


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')

    # Set initial argument values
    q.client.theme_dark = True

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for the main page
    q.page['table'] = cards.table()

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


@on('transactions')
@on('view_transaction')
async def view_transaction(q: Q):
    """
    View transaction.
    """

    logging.info('Viewing transaction')

    # Remove multiselection
    q.page['table'].items[0].table.multiple = False
    q.page['table'].items[1].buttons.items[1].button.name = 'multiselect'
    q.page['table'].items[1].buttons.items[1].button.label = 'Multiselect'

    # Display row information in a dialog
    rows = [int(i) for i in q.args.transactions] if q.args.transactions else [int(q.args.view_transaction)]

    q.page['meta'].dialog = cards.dialog_transaction(rows=rows)

    await q.page.save()


@on('view_image')
async def view_image(q: Q):
    """
    View image.
    """

    logging.info('Viewing image')

    # Display image in a dialog
    q.page['meta'].dialog = cards.dialog_image(row=int(q.args.view_image))

    await q.page.save()


@on('paginate')
async def paginate(q: Q):
    """
    Enable pagination.
    """

    logging.info('Enabling pagination')

    # Enable pagination in the table
    q.page['table'] = cards.table(pagination=True)
    q.page['table'].items[0].table.rows = cards.update_table_rows(page_offset=0)

    await q.page.save()


@on('unpaginate')
async def paginate(q: Q):
    """
    Disable pagination.
    """

    logging.info('Disabling pagination')

    # Disable pagination in the table
    q.page['table'] = cards.table()

    await q.page.save()


async def update_table(q: Q):
    """
    Update table.
    """

    logging.info('Updating table')

    # Update table with page change
    page_offset = q.events.transactions.page_change.get('offset', 0)

    q.page['table'].items[0].table.rows = cards.update_table_rows(page_offset=page_offset)

    await q.page.save()


@on('multiselect')
async def multiselect(q: Q):
    """
    Enable multiselection.
    """

    logging.info('Enabling multiselection')

    # Enable multiselection in the table
    q.page['table'].items[0].table.multiple = True
    q.page['table'].items[1].buttons.items[1].button.name = 'view_transactions'
    q.page['table'].items[1].buttons.items[1].button.label = 'View'

    await q.page.save()


@on('dialog_image.dismissed')
@on('dialog_transaction.dismissed')
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
