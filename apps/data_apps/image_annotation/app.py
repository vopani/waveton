import logging
from random import randint
import json
from h2o_wave import Q, main, app, copy_expando, handle_on, on, site

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

        # Update image if resized
        elif q.args.image_height is not None and q.args.image_height != q.client.image_height:
            await resize_image(q)

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

    q.app.cards = ['image_classes', 'image_annotator', 'error']

    q.app.image_path, = await q.site.upload([constants.IMAGE_PATH])


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')

    # Set initial argument values
    q.client.theme_dark = True

    q.client.image_path = q.app.image_path
    q.client.image_tags = constants.IMAGE_TAGS
    q.client.image_items = constants.IMAGE_ITEMS
    q.client.image_height = constants.IMAGE_HEIGHT

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for main page
    q.page['image_classes'] = cards.image_classes(
        image_tags=q.client.image_tags,
        image_height=q.client.image_height
    )
    q.page['image_annotator'] = cards.image_annotator(
        image_path=q.client.image_path,
        image_tags=q.client.image_tags,
        image_items=q.client.image_items,
        image_height=q.client.image_height
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
async def add_class(q: Q):
    """
    Add a new class to image classes.
    """

    logging.info('Adding a new class')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.image_items = q.client.image_annotator

    # Add new class
    if len(q.client.new_class_name) > 0:
        q.client.image_tags.append({
            'name': q.client.new_class_name.lower(),
            'label': q.client.new_class_name,
            'color': '#{:02x}{:02x}{:02x}'.format(randint(0, 255), randint(0, 255), randint(0, 255))
        })

    # Refresh data with new class
    q.page['image_classes'] = cards.image_classes(
        image_tags=q.client.image_tags,
        image_height=q.client.image_height
    )
    q.page['image_annotator'] = cards.image_annotator(
        image_path=q.client.image_path,
        image_tags=q.client.image_tags,
        image_items=q.client.image_items,
        image_height=q.client.image_height
    )

    await q.page.save()


@on('delete')
async def delete_class(q: Q):
    """
    Delete a class from image classes.
    """

    logging.info('Deleting a class')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.image_items = q.client.image_annotator

    # Delete class and it's items
    if len(q.client.image_tags) > 1:
        q.client.image_tags = [tag for tag in q.client.image_tags if tag['name'] != q.client.delete_class_name]
        q.client.image_items = [item for item in q.client.image_items if item['tag'] != q.client.delete_class_name]
    else:
        logging.info('No classes deleted since annotator requires at least one class available')

    # Refresh data with remaining classes
    q.page['image_classes'] = cards.image_classes(
        image_tags=q.client.image_tags,
        image_height=q.client.image_height
    )
    q.page['image_annotator'] = cards.image_annotator(
        image_path=q.client.image_path,
        image_tags=q.client.image_tags,
        image_items=q.client.image_items,
        image_height=q.client.image_height
    )

    await q.page.save()


async def resize_image(q: Q):
    """
    Resize image height.
    """

    logging.info('Resizing height of the image')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.image_items = q.client.image_annotator

    # Refresh data with new height of image
    q.page['image_classes'] = cards.image_classes(
        image_tags=q.client.image_tags,
        image_height=q.client.image_height
    )
    q.page['image_annotator'] = cards.image_annotator(
        image_path=q.client.image_path,
        image_tags=q.client.image_tags,
        image_items=q.client.image_items,
        image_height=q.client.image_height
    )

    await q.page.save()


@on('new_image')
async def new_image(q: Q):
    """
    Add a new image.
    """

    logging.info('Adding a new image')

    q.page['meta'].dialog = cards.dialog_new_image

    await q.page.save()


@on('upload')
async def upload_image(q: Q):
    """
    Upload image.
    """

    logging.info('Uploading new image')

    # Update to new image
    q.client.image_path = q.args.upload[0]
    q.client.image_items = None
    q.client.image_height = constants.IMAGE_HEIGHT

    # Remove dialog
    q.page['meta'].dialog = None

    # Refresh data with new image
    q.page['image_classes'] = cards.image_classes(
        image_tags=q.client.image_tags,
        image_height=q.client.image_height
    )
    q.page['image_annotator'] = cards.image_annotator(
        image_path=q.client.image_path,
        image_tags=q.client.image_tags,
        image_items=q.client.image_items,
        image_height=q.client.image_height
    )

    await q.page.save()


@on('download')
async def download(q: Q):
    """
    Download annotated image as json.
    """

    logging.info('Downloading annotations in JSON')

    # Save annotation
    copy_expando(q.args, q.client)
    q.client.image_items = q.client.image_annotator

    annotations_file = 'annotations.json'

    with open(annotations_file, 'w') as outfile:
        outfile.write(json.dumps(q.client.image_items))

    annotations_path, = await q.site.upload([annotations_file])

    q.page['meta'].redirect = annotations_path

    await q.page.save()


@on('dialog_new_image.dismissed')
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
