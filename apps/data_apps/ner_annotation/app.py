import logging
from random import randint

from h2o_wave import Q, main, app, copy_expando, handle_on, on

import cards
import constants

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
            q.app.initialized = True

        # Initialize the client (browser tab) if not already
        if not q.client.initialized:
            await initialize_client(q)
            q.client.initialized = True

        # Update theme if toggled
        elif q.args.theme_dark is not None and q.args.theme_dark != q.client.theme_dark:
            await update_theme(q)

        # Delegate query to query handlers
        elif await handle_on(q):
            pass

        # Adding this condition to help in identifying bugs (instead of seeing a blank page in the browser)
        else:
            await handle_fallback(q)

    except Exception as error:
        await show_error(q, error=str(error))


async def initialize_app(q: Q):
    """
    Initialize the app.
    """

    logging.info('Initializing app')

    q.app.cards = ['ner_entities', 'ner_annotator', 'error']


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')

    # Set initial argument values
    q.client.theme_dark = True

    q.client.ner_tags = constants.NER_TAGS
    q.client.ner_data = constants.NER_DATA
    q.client.ner_index = 0
    q.client.disable_next = False
    q.client.disable_previous = True

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for main page
    q.page['ner_entities'] = cards.ner_entities(ner_tags=q.client.ner_tags)
    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index],
        disable_next=q.client.disable_next,
        disable_previous=q.client.disable_previous
    )

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


@on('next')
async def show_next_text(q: Q):
    """
    Show next NER data.
    """

    logging.info('Showing the next NER data')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.ner_data[q.client.ner_index] = q.client.ner_annotator

    # Move to next text
    q.client.ner_index += 1
    q.client.disable_previous = False

    # Disable 'Next' if last text
    if q.client.ner_index == len(q.client.ner_data) - 1:
        q.client.disable_next = True

    # Display data
    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index],
        disable_next=q.client.disable_next,
        disable_previous=q.client.disable_previous
    )

    await q.page.save()


@on('previous')
async def show_previous_text(q: Q):
    """
    Show previous NER data.
    """

    logging.info('Showing the previous NER data')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.ner_data[q.client.ner_index] = q.client.ner_annotator

    # Move to previous text
    q.client.ner_index -= 1
    q.client.disable_next = False

    # Disable 'Previous' if first text
    if q.client.ner_index == 0:
        q.client.disable_previous = True

    # Display data
    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index],
        disable_next=q.client.disable_next,
        disable_previous=q.client.disable_previous
    )

    await q.page.save()


@on('add')
async def add_entity(q: Q):
    """
    Add a new entity to NER tags.
    """

    logging.info('Adding a new entity')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.ner_data[q.client.ner_index] = q.client.ner_annotator

    # Add new entity
    if len(q.client.new_entity_name) > 0:
        q.client.ner_tags.append({
            'name': q.client.new_entity_name.lower(),
            'label': q.client.new_entity_name,
            'color': '#{:02x}{:02x}{:02x}'.format(randint(0, 255), randint(0, 255), randint(0, 255))
        })

    # Refresh data with new entity
    q.page['ner_entities'] = cards.ner_entities(ner_tags=q.client.ner_tags)
    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index],
        disable_next=q.client.disable_next,
        disable_previous=q.client.disable_previous
    )

    await q.page.save()


@on('delete')
async def delete_entity(q: Q):
    """
    Delete an entity from NER tags.
    """

    logging.info('Deleting an entity')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.ner_data[q.client.ner_index] = q.client.ner_annotator

    # Delete entity and it's tags
    if len(q.client.ner_tags) > 1:
        q.client.ner_tags = [tag for tag in q.client.ner_tags if tag['name'] != q.client.delete_entity_name]
        for text in q.client.ner_data:
            for item in text:
                if 'tag' in item.keys():
                    if item['tag'] == q.client.delete_entity_name:
                        item.pop('tag')
    else:
        logging.info('No entities deleted since annotator requires at least one entity available')

    # Refresh data with remaining entities
    q.page['ner_entities'] = cards.ner_entities(ner_tags=q.client.ner_tags)
    q.page['ner_annotator'] = cards.ner_annotator(
        ner_tags=q.client.ner_tags,
        ner_items=q.client.ner_data[q.client.ner_index],
        disable_next=q.client.disable_next,
        disable_previous=q.client.disable_previous
    )

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
    Reset the client (browser tab).
    This function is called when the user clicks "Reload" on the crash report.
    """

    logging.info('Reloading client')

    # Clear all cards
    clear_cards(q, q.app.cards)

    # Reload the client
    await initialize_client(q)


async def handle_fallback(q: Q):
    """
    Handle fallback cases.
    This function should never get called unless there is a bug in our code or query handling logic.
    """

    logging.info('Adding fallback page')

    q.page['fallback'] = cards.fallback

    await q.page.save()
