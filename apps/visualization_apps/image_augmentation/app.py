import logging
from random import randint
import json
from h2o_wave import Q, main, app, copy_expando, handle_on, on
import cv2
import cards
import constants
import albumentations as A

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

        # Initialize the client (browser tab) if not already
        if not q.client.initialized:
            await initialize_client(q)

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

    # Set initial argument values
    q.app.cards = ['image_classes','aug_image_card','image_card', 'image_annotator', 'error']

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

    q.client.prompt = constants.PROMPTS[0]
    q.client.image_resize = constants.RESIZE_RATIO

    q.user.template_image_path, = await q.site.upload(['generated/xray1.png'])
    q.client.img = cv2.imread("generated/xray1.png")
    q.client.aug_img = cv2.imread("generated/xray1.png")
    q.user.aug_image_path = q.user.template_image_path
    q.client.augs_type_list = constants.AUGS_TYPES_LIST
    q.client.dropdown_name = constants.DROPDOWN_NAME[0]

    q.client.selected_augs = []

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.template_image_path)

    q.page['options_card'] = cards.options_card(q.client.augs_type_list,prompt=q.client.prompt,dropdown_name=q.client.dropdown_name)


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


@on('resize_images')
async def resize_images(q: Q):
    copy_expando(q.args, q.client)

    logging.info('Showing the resized image')
    q.client.image_resize = q.client.resize_image_ratio

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_path)

    await q.page.save()


@on('select_type_button')
async def select_type(q: Q):
    copy_expando(q.args, q.client)

    q.client.transform = None
    q.client.prompt = constants.PROMPTS[1]
    q.client.dropdown_name = constants.DROPDOWN_NAME[1]

    if q.client.select_new_aug == 'Hard Augs':
        q.page['options_card'] = cards.options_card(constants.HARD_AUGS_LIST,prompt=q.client.prompt,dropdown_name=q.client.dropdown_name)
    else:
        q.page['options_card'] = cards.options_card(constants.SOFT_AUGS_LIST,prompt=q.client.prompt,dropdown_name=q.client.dropdown_name)


    q.user.aug_image_path = q.user.template_image_path

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_path)

    await q.page.save()


@on('select_aug_button')
async def show_augs(q: Q):
    copy_expando(q.args, q.client)

    param_values = {"p": 1.0}

    q.client.selected_augs.append(getattr(A, q.client.select_new_aug)(**param_values))
    logging.info(q.client.selected_augs)
    # q.page['options_card'] = cards.options_card(q.client.augs_type_list)

    q.client.transform = A.ReplayCompose(q.client.selected_augs)
    transformed_image = q.client.transform(image=q.client.aug_img)["image"]

    cv2.imwrite("generated/aug.png", transformed_image)
    q.user.aug_image_path, = await q.site.upload(["generated/aug.png"])

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_path)

    await q.page.save()


@on('reset_aug_button')
async def reset_augs(q: Q):
    copy_expando(q.args, q.client)

    q.client.selected_augs = []
    logging.info(q.client.selected_augs)
    q.client.transform = None
    q.client.prompt = constants.PROMPTS[0]
    q.client.dropdown_name = constants.DROPDOWN_NAME[0]
    q.page['options_card'] = cards.options_card(q.client.augs_type_list,prompt=q.client.prompt,dropdown_name=q.client.dropdown_name)

    q.user.aug_image_path = q.user.template_image_path

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_path)

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
    q.client.transform = None
    q.client.image_resize = constants.RESIZE_RATIO

    # Remove dialog
    q.page['meta'].dialog = None
    q.client.prompt = constants.PROMPTS[0]
    q.client.dropdown_name = constants.DROPDOWN_NAME[0]
    q.page['options_card'] = cards.options_card(q.client.augs_type_list,prompt=q.client.prompt,dropdown_name=q.client.dropdown_name)

    q.user.aug_image_path = q.client.image_path
    q.user.template_image_path = q.client.image_path

    q.client.img = cv2.imread(q.client.image_path)
    q.client.aug_img = cv2.imread(q.client.image_path.split(' ')[-1])

    logging.info(q.client.image_path)
    logging.info(''.join(q.client.image_path.split('/')[2:]))

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_path)


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
