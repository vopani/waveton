import logging

from h2o_wave import Q, main, app, expando_to_dict, handle_on, on

import cards

logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)


@app('/')
async def serve(q: Q):
    """
    App function.
    """

    try:
        # initialize app
        if not q.app.app_initialized:
            await initialize_app(q)

        # initialize client
        if not q.client.client_initialized:
            await initialize_client(q)

        # handle ons
        elif await handle_on(q):
            pass

        # dummy update for edge cases
        else:
            await update_dummy(q)

    except Exception as error:
        await handle_error(q, error=str(error))


async def initialize_app(q: Q):
    """
    Initializing app.
    """

    logging.info('Initializing app')

    q.app.app_initialized = True


async def initialize_client(q: Q):
    """
    Initializing client.
    """

    logging.info('Initializing client')

    q.client.theme_dark = True

    q.page['meta'] = cards.meta()
    q.page['header'] = cards.header()
    q.page['home'] = cards.home()
    q.page['footer'] = cards.footer()

    q.page['dummy'] = cards.dummy()

    q.client.client_initialized = True

    await q.page.save()


async def drop_cards(q: Q, card_names: list):
    """
    Drop cards from Wave page.
    """

    logging.info('Clearing cards')

    for card_name in card_names:
        del q.page[card_name]


async def handle_error(q: Q, error: str):
    """
    Handle any app error.
    """

    logging.error(error)

    await drop_cards(q, cards.DROPPABLE_CARDS)

    q.page['error'] = cards.error(
        q_app=expando_to_dict(q.app),
        q_user=expando_to_dict(q.user),
        q_client=expando_to_dict(q.client),
        q_events=expando_to_dict(q.events),
        q_args=expando_to_dict(q.args)
    )

    await q.page.save()


@on('restart')
async def restart(q: Q):
    """
    Restart app.
    """

    logging.info('Restarting app')

    await initialize_client(q)


@on('report')
async def report(q: Q):
    """
    Report error details.
    """

    logging.info('Displaying error details')

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


async def update_dummy(q: Q):
    """
    Dummy update for edge cases.
    """

    logging.info('Adding dummy page')

    q.page['dummy'].items = []

    await q.page.save()
