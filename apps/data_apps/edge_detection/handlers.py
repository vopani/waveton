from h2o_wave import Q, on

from actions import drop_cards, update_theme
from constants import DROPPABLE_CARDS, DEFAULT_LOGGER
from initializers import initialize_client


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
async def theme_dark(q: Q):
    q.client.theme_dark = q.args.theme_dark
    await update_theme(q)
