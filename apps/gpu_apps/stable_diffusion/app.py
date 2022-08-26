import base64
import logging

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from h2o_wave import Q, main, app, copy_expando, handle_on, on

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

    q.app.cards = ['main', 'error']

    q.app.access_token = ''


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

    # Add cards for the main page
    if not torch.cuda.is_available():
        q.page['main'] = cards.gpu
    elif q.app.access_token == '':
        q.page['main'] = cards.setup
    else:
        q.page['main'] = cards.main

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


@on('save')
async def save(q: Q):
    """
    Save access token.
    """

    logging.info('Saving access token')

    q.app.access_token = q.args.access_token

    try:
        q.app.model = StableDiffusionPipeline.from_pretrained(
            'CompVis/stable-diffusion-v1-4',
            use_auth_token=q.app.access_token
        ).to('cuda')

        await initialize_client(q)
    except Exception as e:
        logging.info(e)

        q.page['main'].items[0].textbox.error = '''
            Unable to access Stable Diffusion model. Please double check token and accept model license.
        '''

        await q.page.save()


@on('generate')
async def generate(q: Q):
    """
    Generate images from prompt.
    """

    logging.info('Generating images')

    with autocast('cuda'):
        image = q.app.model(q.args.prompt)['sample'][0]

    image.save('sd_image.png')

    sd_image_path, = await q.site.upload(['sd_image.png'])

    q.page['main'].items[2].separator.label = q.args.prompt
    q.page['main'].items[3].inline.items[0].image.visible = True
    q.page['main'].items[3].inline.items[0].image.path = sd_image_path

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
