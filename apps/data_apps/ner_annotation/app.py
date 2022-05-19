import logging
from random import randint

from h2o_wave import Q, main, app, copy_expando, expando_to_dict, handle_on, on

import cards
import constants

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
            await setup_home(q)

        # set theme
        elif q.args.theme_dark is not None and q.args.theme_dark != q.client.theme_dark:
            await update_theme(q)

        # show next text
        elif q.args.next:
            await show_next_text(q)

        # show previous text
        elif q.args.previous:
            await show_previous_text(q)

        # add entity
        elif q.args.add:
            await add_entity(q)

        # delete entity
        elif q.args.delete:
            await delete_entity(q)

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

    q.client.ner_tags = constants.NER_TAGS
    q.client.ner_data = constants.NER_DATA
    q.client.ner_index = 0

    q.client.client_initialized = True

    await q.page.save()


async def setup_home(q: Q):
    """
    Set up home page of app.
    """

    q.page['meta'] = cards.meta()
    q.page['header'] = cards.header()
    q.page['ner_entities'] = cards.ner_entities(ner_tags=q.client.ner_tags)
    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index]
    )
    q.page['footer'] = cards.footer()

    q.page['dummy'] = cards.dummy()

    await q.page.save()


async def update_theme(q: Q):
    """
    Update theme of app.
    """

    copy_expando(q.args, q.client)

    if q.client.theme_dark:
        logging.info('Updating theme to dark mode')

        q.page['meta'].theme = 'h2o-dark'
        q.page['header'].icon_color = 'black'
    else:
        logging.info('Updating theme to light mode')

        q.page['meta'].theme = 'light'
        q.page['header'].icon_color = '#FEC924'

    q.page['header'].items[0].toggle.value = q.client.theme_dark

    await q.page.save()


async def show_next_text(q: Q):
    """
    Show next NER data.
    """

    logging.info('Showing the next NER data')

    copy_expando(q.args, q.client)
    q.client.ner_data[q.client.ner_index] = q.client.ner_annotator

    if q.client.ner_index == len(q.client.ner_data) - 1:
        q.client.ner_index = 0
    else:
        q.client.ner_index += 1

    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index]
    )

    await q.page.save()


async def show_previous_text(q: Q):
    """
    Show previous NER data.
    """

    logging.info('Showing the previous NER data')

    copy_expando(q.args, q.client)
    q.client.ner_data[q.client.ner_index] = q.client.ner_annotator

    if q.client.ner_index == 0:
        q.client.ner_index = len(q.client.ner_data) - 1
    else:
        q.client.ner_index -= 1

    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index]
    )

    await q.page.save()


async def add_entity(q: Q):
    """
    Add a new entity to NER tags.
    """

    logging.info('Adding a new entity')

    copy_expando(q.args, q.client)
    q.client.ner_data[q.client.ner_index] = q.client.ner_annotator

    if len(q.client.new_entity_name) > 0:
        q.client.ner_tags.append({
            'name': q.client.new_entity_name.lower(),
            'label': q.client.new_entity_name,
            'color': '#{:02x}{:02x}{:02x}'.format(randint(0, 255), randint(0, 255), randint(0, 255))
        })

    q.page['ner_entities'] = cards.ner_entities(ner_tags=q.client.ner_tags)
    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index]
    )

    await q.page.save()


async def delete_entity(q: Q):
    """
    Delete an entity from NER tags.
    """

    logging.info('Deleting an entity')

    copy_expando(q.args, q.client)
    q.client.ner_data[q.client.ner_index] = q.client.ner_annotator

    if len(q.client.ner_tags) > 1:
        q.client.ner_tags = [tag for tag in q.client.ner_tags if tag['name'] != q.client.delete_entity_name]
        for text in q.client.ner_data:
            for item in text:
                if 'tag' in item.keys():
                    if item['tag'] == q.client.delete_entity_name:
                        item.pop('tag')

    q.page['ner_entities'] = cards.ner_entities(ner_tags=q.client.ner_tags)
    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index]
    )

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

    await drop_cards(q, cards.DROPPABLE_CARDS)

    await initialize_client(q)
    await setup_home(q)


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
