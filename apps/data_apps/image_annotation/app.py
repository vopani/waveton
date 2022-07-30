import logging
from random import randint
import json
import pandas as pd
from h2o_wave import Q, main, app, copy_expando, handle_on, on, site, ui

import cards
import constants
# import os
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

    q.app.cards = ['image_entities', 'image_annotator', 'error']


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')

    # Set initial argument values
    q.client.theme_dark = True

    q.client.image_tags = constants.IMAGE_TAGS
    q.client.image_data = constants.IMAGES
    q.client.image_items = constants.IMAGE_ITEMS
    q.client.image_pixel = constants.IMAGE_PIXEL
    q.client.image_index = 0

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer
    # q.page['msg'] = ui.message_bar(type='success', text='Downloaded Json Successfully!!'),

    # Add cards for main page
    q.page['image_entities'] = cards.image_entities(image_tags=q.client.image_tags)

    q.page['image_annotator'] = cards.image_annotator(
        image_tags=q.client.image_tags,
        image_items= q.client.image_items,
        images=q.client.image_data[q.client.image_index],
        image_pixels = q.client.image_pixel
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



@on('add')
async def add_entity(q: Q):
    """
    Add a new entity to Image Classes.
    """

    logging.info('Adding a new class')

    # Save annotation
    copy_expando(q.args, q.client)

    old_annotation = []
    for en,cnxt in enumerate(q.client.annotator):
        x1 = cnxt['shape']['rect']['x1']
        y1 = cnxt['shape']['rect']['y1']
        x2 = cnxt['shape']['rect']['x2']
        y2 = cnxt['shape']['rect']['y2']
        old_annotation.append(ui.image_annotator_item(shape=ui.image_annotator_rect(x1,y1,x2,y2),tag=cnxt['tag']))

    q.client.image_items = old_annotation

    logging.info(q.client)
    logging.info('ok')
    # Add new entity
    if len(q.client.add_new_class) > 0:
        q.client.image_tags.append({
            'name': q.client.add_new_class.lower(),
            'label': q.client.add_new_class,
            'color': '#{:02x}{:02x}{:02x}'.format(randint(0, 255), randint(0, 255), randint(0, 255))
        })

    # Refresh data with new entity
    q.page['image_entities'] = cards.image_entities(image_tags=q.client.image_tags)
    q.page['image_annotator'] = cards.image_annotator(
        image_tags=q.client.image_tags,
        image_items= q.client.image_items,
        images=q.client.image_data[q.client.image_index],
        image_pixels=q.client.image_pixel

    )

    await q.page.save()

@on('file_upload')
async def add_image(q: Q):
    """
    Add a new Image to Annotate.
    """

    logging.info('Adding a new Image')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.image_items = []

    logging.info('done')
    q.client.image_data[q.client.image_index] = q.client.file_upload[0]
    logging.info(q.client.file_upload[0])

    # Refresh data with new entity
    q.page['image_entities'] = cards.image_entities(image_tags=q.client.image_tags)
    q.page['image_annotator'] = cards.image_annotator(
        image_tags=q.client.image_tags,
        image_items= q.client.image_items,
        images=q.client.image_data[q.client.image_index],
        image_pixels=q.client.image_pixel

    )

    await q.page.save()


@on('change_pixel')
async def add_image(q: Q):

    logging.info('Changing Size of Image')

    # Save annotation
    copy_expando(q.args, q.client)

    q.client.image_pixel = q.client.new_pixel_size

    # Refresh data with new entity
    q.page['image_entities'] = cards.image_entities(image_tags=q.client.image_tags)
    q.page['image_annotator'] = cards.image_annotator(
        image_tags=q.client.image_tags,
        image_items= [],
        images=q.client.image_data[q.client.image_index],
        image_pixels=q.client.image_pixel

    )
    logging.info('done')

    await q.page.save()



@on('delete')
async def delete_entity(q: Q):


    logging.info('Deleting an entity')

    # Save annotation
    copy_expando(q.args, q.client)

    old_annotation = []
    for en,cnxt in enumerate(q.client.annotator):
        if cnxt['tag'] == q.client.delete_existing_class:
            logging.info('skipping this class')
            continue
        x1 = cnxt['shape']['rect']['x1']
        y1 = cnxt['shape']['rect']['y1']
        x2 = cnxt['shape']['rect']['x2']
        y2 = cnxt['shape']['rect']['y2']
        old_annotation.append(ui.image_annotator_item(shape=ui.image_annotator_rect(x1,y1,x2,y2),tag=cnxt['tag']))

    q.client.image_items = old_annotation

    if len(q.client.image_tags) > 1:
        q.client.image_tags = [tag for tag in q.client.image_tags if tag['name'] != q.client.delete_existing_class]
    else:
        logging.info('Please have at least one class!!')

    # Refresh data with remaining entities
    q.page['image_entities'] = cards.image_entities(image_tags=q.client.image_tags)
    q.page['image_annotator'] = cards.image_annotator(
        image_tags=q.client.image_tags,
        image_items= q.client.image_items,
        images=q.client.image_data[q.client.image_index],
        image_pixels=q.client.image_pixel

    )

    await q.page.save()

@on('save_output')
async def save_output(q: Q):
    """
    Add a new Image to Annotate.
    """

    logging.info('Downloading the Annotations in CSV')

    # Save annotation
    copy_expando(q.args, q.client)

    logging.info('starting')

    annotation_list = q.client.annotator
    # filename = q.client.textbox_suffix
    output_path = "output/annotations.csv"
    final = open(output_path, "w")
    # json.dump(annotation_list,final)



    with final as output_file:
        pd.DataFrame(annotation_list).to_csv(output_file,index=False)
        # json.dump(annotation_list, output_file)


    logging.info('Downloading dataset')

    download_path, = await q.site.upload([output_path])

    q.page['meta'].redirect = download_path


    old_annotation = []
    for en,cnxt in enumerate(q.client.annotator):
        x1 = cnxt['shape']['rect']['x1']
        y1 = cnxt['shape']['rect']['y1']
        x2 = cnxt['shape']['rect']['x2']
        y2 = cnxt['shape']['rect']['y2']
        old_annotation.append(ui.image_annotator_item(shape=ui.image_annotator_rect(x1,y1,x2,y2),tag=cnxt['tag']))

    q.client.image_items = old_annotation

    logging.info(q.client)
    logging.info('ok')
    # Add new entity
    if len(q.client.add_new_class) > 0:
        q.client.image_tags.append({
            'name': q.client.add_new_class.lower(),
            'label': q.client.add_new_class,
            'color': '#{:02x}{:02x}{:02x}'.format(randint(0, 255), randint(0, 255), randint(0, 255))
        })

    # Refresh data with new entity
    q.page['image_entities'] = cards.image_entities(image_tags=q.client.image_tags)
    q.page['image_annotator'] = cards.image_annotator(
        image_tags=q.client.image_tags,
        image_items= q.client.image_items,
        images=q.client.image_data[q.client.image_index],
        image_pixels=q.client.image_pixel

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

    # Clear all cards from the page
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
