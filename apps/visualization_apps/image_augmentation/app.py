import logging
import os

import albumentations as A
import cv2
from h2o_wave import Q, main, app, copy_expando, expando_to_dict, handle_on, on

import cards
import constants

# Set up logging
logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)


@app('/')
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """
    print(q.args)
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

        # Update augmented images if any augmentation is changed
        elif any([q.args[augmentation] is not None for augmentation in constants.AUGMENTATIONS]):
            await update_augmented_images(q)

        # Update augmented images if number of images is changed
        elif q.args.images is not None and q.args.images != q.client.images:
            await update_augmented_images(q)

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
    q.app.default_image = cv2.imread('sample.jpeg')
    q.app.default_image_path, = await q.site.upload(files=['sample.jpeg'])

    q.app.initialized = True


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """
    logging.info('Initializing client')

    # Set initial argument values
    q.client.theme_dark = True
    q.client.tab = 'light'
    q.client.base_image_path = q.app.default_image_path
    q.client.base_image = q.app.default_image
    q.client.images = 2
    q.client.augmented_image_paths = [q.client.base_image_path] * q.client.images
    q.client.augmentations = []
    for augmentation in constants.AUGMENTATIONS:
        q.client[augmentation] = False

    # Add layouts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for the main page
    q.page['augmentations'] = cards.augmentations(tab=q.client.tab, augs=q.client.augmentations)
    q.page['images'] = cards.images(
        base_image_path=q.client.base_image_path,
        augmented_image_paths=q.client.augmented_image_paths,
        n_images=q.client.images,
        augs=q.client.augmentations
    )

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
    q.page['augmentations'] = cards.augmentations(tab=q.client.tab, augs=q.client.augmentations)

    await q.page.save()


@on('new_image')
async def upload_new(q: Q):
    """
    Add a new image.
    """
    logging.info('Adding a new image')

    q.page['meta'].dialog = cards.dialog_new_image

    await q.page.save()


@on('upload')
async def upload(q: Q):
    """
    Upload new image.
    """
    logging.info('Uploading new image')

    # Remove dialog
    q.page['meta'].dialog = None

    # Update image
    q.client.base_image_path = q.args.upload[0]
    q.client.base_image = cv2.imread(await q.site.download(q.client.base_image_path, '.'))

    await update_augmented_images(q)


@on('reset')
async def reset_augmentations(q: Q):
    """
    Reset augmentations.
    """
    logging.info('Resetting augmentations')

    # Clearing all augmentations
    q.client.augmentations = []
    for augmentation in constants.AUGMENTATIONS:
        q.client[augmentation] = False

    # Default image
    q.client.augmented_image_paths = [q.client.base_image_path] * q.client.images

    # Update augmentations and images
    q.page['augmentations'] = cards.augmentations(tab=q.client.tab, augs=q.client.augmentations)
    q.page['images'] = cards.images(
        base_image_path=q.client.base_image_path,
        augmented_image_paths=q.client.augmented_image_paths,
        n_images=q.client.images,
        augs=q.client.augmentations
    )

    await q.page.save()


async def update_augmented_images(q: Q):
    """
    Update augmented images.
    """
    logging.info('Updating augmented images')

    # Save settings
    copy_expando(q.args, q.client)
    q.client.augmentations = sorted(
        [augmentation for augmentation in constants.AUGMENTATIONS if q.client[augmentation]]
    )
    # Set Default probability as 1.0
    param_values = {"p": 1.0}
    # Compile list of augmentations
    augmentations = [getattr(A, augmentation)(**param_values) for augmentation in q.client.augmentations]

    if len(augmentations) == 0:
        # Default image if no augmentations
        q.client.augmented_image_paths = [q.client.base_image_path] * q.client.images
    else:
        # Generate augmented images
        augmentation = A.ReplayCompose(augmentations)
        for i in range(q.client.images):
            augmented_image = augmentation(image=q.client.base_image)['image']
            cv2.imwrite(f'augmented_image_{i+1}.png', augmented_image)

        # Upload images to Wave server
        q.client.augmented_image_paths = await q.site.upload(
            [f'augmented_image_{i+1}.png' for i in range(q.client.images)]
        )

        # Remove images locally
        for i in range(q.client.images):
            os.remove(f'augmented_image_{i+1}.png')

    # Update images
    q.page['images'] = cards.images(
        base_image_path=q.client.base_image_path,
        augmented_image_paths=q.client.augmented_image_paths,
        n_images=q.client.images,
        augs=q.client.augmentations
    )

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
