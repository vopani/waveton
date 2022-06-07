import logging

from h2o_wave import Q, main, app, handle_on, on

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
            q.app.initialized = True  # Mark as initialized at the app level (global to all clients)

        # Initialize the client (browser tab) if not already
        if not q.client.initialized:
            await initialize_client(q)
            q.client.initialized = True  # Mark as initialized at the client (browser tab) level

        # Delegate query to query handlers
        elif await handle_on(q):
            pass

        # This condition should never execute unless there is a bug in our code
        # Adding this condition here helps us identify those cases (instead of seeing a blank page in the browser)
        else:
            await handle_fallback(q)

    except Exception as error:
        await show_error(q, error=str(error))


async def initialize_app(q: Q):
    """
    Initialize the app.
    """

    logging.info('Initializing app')

    # Add app-level initialization logic here (loading datasets, database connections, etc.)


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for the home page
    q.page['home'] = cards.home

    # Add more cards to the home page

    # Save the page
    await q.page.save()


def clear_cards(q: Q, card_names: list):
    """
    Clear cards from the page.
    """

    logging.info('Clearing cards')

    for card_name in card_names:
        del q.page[card_name]


async def show_error(q: Q, error: str):
    """
    Displays errors.
    """

    logging.error(error)

    # Clear all cards from the page
    clear_cards(q, ['home'])

    # Format and display the error
    q.page['error'] = cards.create_crash_report(q)

    await q.page.save()


@on('reload')
async def reload_client(q: Q):
    """
    Reset the client (browser tab).
    This function is called when the user clicks "Reload" on the crash report.
    """

    logging.info('Reloading client')

    await initialize_client(q)


async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    This function should never get called unless there is a bug in our code or query handling logic.
    """

    logging.info('Adding fallback page')

    q.page['fallback'] = cards.fallback

    await q.page.save()
