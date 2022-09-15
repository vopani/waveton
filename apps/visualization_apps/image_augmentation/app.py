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
    q.app.cards = ['extra_img_options_card','current_light_augs_buttons_card','current_hard_augs_buttons_card','aug_image_card','image_card', 'error']

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

    q.client.image_resize = constants.RESIZE_RATIO

    q.user.template_image_path, = await q.site.upload(['generated/xray1.png'])
    q.client.img = cv2.imread("generated/xray1.png")
    q.client.aug_img = cv2.imread("generated/xray1.png")
    q.user.aug_image_path = q.user.template_image_path

    q.client.num_images = 4
    q.user.aug_image_paths = [q.user.template_image_path for i in range(q.client.num_images)]

    q.client.light_augs_list = constants.LIGHT_AUGS_LIST
    q.client.hard_augs_list = constants.HARD_AUGS_LIST
    q.user.p_value = 1.0
    q.client.selected_augs = []
    q.client.selected_hard_augs_name = []
    q.client.selected_light_augs_name = []

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_paths)
    q.page['options_card'] = cards.options_card(q.client.light_augs_list,q.client.hard_augs_list)
    q.page['current_light_augs_buttons_card'] = cards.current_light_augs_buttons_card(q.client.selected_light_augs_name)
    q.page['current_hard_augs_buttons_card'] = cards.current_hard_augs_buttons_card(q.client.selected_hard_augs_name)
    q.page['extra_img_options_card'] = cards.extra_img_options_card()

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
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_paths)

    await q.page.save()


@on('num_aug_images_button')
async def show_augs(q: Q):
    copy_expando(q.args, q.client)
    q.client.num_images = q.client.num_aug_images
    q.user.aug_image_paths = []
    for i in range(q.client.num_images):
        q.client.transform = A.ReplayCompose(q.client.selected_augs)
        transformed_image = q.client.transform(image=q.client.aug_img)["image"]
        cv2.imwrite(f"generated/aug_{i}.png", transformed_image)
        q.user.aug_image_path, = await q.site.upload([f"generated/aug_{i}.png"])
        q.user.aug_image_paths.append(q.user.aug_image_path)

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_paths)
    q.page['current_light_augs_buttons_card'] = cards.current_light_augs_buttons_card(q.client.selected_light_augs_name)
    q.page['current_hard_augs_buttons_card'] = cards.current_hard_augs_buttons_card(q.client.selected_hard_augs_name)
    await q.page.save()


@on('select_light_aug_button')
async def show_augs(q: Q):
    copy_expando(q.args, q.client)

    param_values = {"p": q.client.slider_p_value_light}

    q.client.selected_augs.append(getattr(A, q.client.select_light_aug)(**param_values))
    q.client.selected_light_augs_name.append(q.client.select_light_aug)

    q.user.aug_image_paths = []
    for i in range(q.client.num_images):
        q.client.transform = A.ReplayCompose(q.client.selected_augs)
        transformed_image = q.client.transform(image=q.client.aug_img)["image"]
        cv2.imwrite(f"generated/aug_{i}.png", transformed_image)
        q.user.aug_image_path, = await q.site.upload([f"generated/aug_{i}.png"])
        q.user.aug_image_paths.append(q.user.aug_image_path)

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_paths)
    q.page['current_light_augs_buttons_card'] = cards.current_light_augs_buttons_card(q.client.selected_light_augs_name)
    q.page['current_hard_augs_buttons_card'] = cards.current_hard_augs_buttons_card(q.client.selected_hard_augs_name)
    await q.page.save()


@on('select_hard_aug_button')
async def show_augs(q: Q):

    copy_expando(q.args, q.client)

    param_values = {"p": q.client.slider_p_value_hard}
    q.client.selected_augs.append(getattr(A, q.client.select_hard_aug)(**param_values))
    q.client.selected_hard_augs_name.append(q.client.select_hard_aug)

    q.user.aug_image_paths = []
    for i in range(q.client.num_images):
        q.client.transform = A.ReplayCompose(q.client.selected_augs)
        transformed_image = q.client.transform(image=q.client.aug_img)["image"]
        cv2.imwrite(f"generated/aug_{i}.png", transformed_image)
        q.user.aug_image_path, = await q.site.upload([f"generated/aug_{i}.png"])
        q.user.aug_image_paths.append(q.user.aug_image_path)


    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_paths)
    q.page['current_light_augs_buttons_card'] = cards.current_light_augs_buttons_card(q.client.selected_light_augs_name)
    q.page['current_hard_augs_buttons_card'] = cards.current_hard_augs_buttons_card(q.client.selected_hard_augs_name)

    await q.page.save()


@on('reset_aug_button')
async def reset_augs(q: Q):
    copy_expando(q.args, q.client)

    q.client.selected_augs = []
    q.client.selected_light_augs_name = []
    q.client.selected_hard_augs_name = []
    q.user.aug_image_paths = [q.user.template_image_path for i in range(q.client.num_images)]
    q.client.transform = None

    q.page['options_card'] = cards.options_card(q.client.augs_type_list)

    q.user.aug_image_path = q.user.template_image_path

    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_paths)
    q.page['current_light_augs_buttons_card'] = cards.current_light_augs_buttons_card(q.client.selected_light_augs_name)
    q.page['current_hard_augs_buttons_card'] = cards.current_hard_augs_buttons_card(q.client.selected_hard_augs_name)
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

    q.page['options_card'] = cards.options_card(q.client.augs_type_list)
    q.client.num_images = 4

    q.user.aug_image_paths = [q.client.image_path + str(i) for i in range(q.client.num_images)]
    q.user.template_image_path = q.client.image_path

    q.client.img = cv2.imread(q.client.image_path)
    q.client.aug_img = cv2.imread(q.client.image_path.split(' ')[-1])

    logging.info(q.client.image_path)
    logging.info(''.join(q.client.image_path.split('/')[2:]))


    q.page['image_card'] = cards.image_card(q.client.image_resize, q.user.template_image_path)
    q.page['aug_image_card'] = cards.aug_image_card(q.client.image_resize, q.user.aug_image_paths)
    q.page['current_light_augs_buttons_card'] = cards.current_light_augs_buttons_card(q.client.selected_light_augs_name)
    q.page['current_hard_augs_buttons_card'] = cards.current_hard_augs_buttons_card(q.client.selected_hard_augs_name)

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
