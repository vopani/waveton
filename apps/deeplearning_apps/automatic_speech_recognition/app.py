import logging

from h2o_wave import Q, main, app, copy_expando, handle_on, on
from transformers import AutoModelForCTC, Wav2Vec2Processor

import cards
from utils import generate_transcription, get_inline_script

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

        # Initialize the client if not already
        if not q.client.initialized:
            await initialize_client(q)

        # Update theme if toggled
        elif q.args.theme_dark is not None and q.args.theme_dark != q.client.theme_dark:
            await update_theme(q)

        # Run inference if audio is recorded
        elif q.events.audio:
            await audio_inference(q)

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

    q.app.cards = ['main', 'error']

    q.app.processor = Wav2Vec2Processor.from_pretrained('facebook/wav2vec2-base-960h')
    q.app.model = AutoModelForCTC.from_pretrained('facebook/wav2vec2-base-960h')

    q.app.initialized = True


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')

    # Set initial argument values
    q.client.theme_dark = True

    # Add layouts, scripts, header and footer
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer

    # Add cards for the main page
    q.page['asr'] = cards.asr()

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


@on('start')
async def start_recording(q: Q):
    """
    Start recording audio.
    """

    logging.info('Starting recording')

    q.page['meta'].script = get_inline_script('startRecording()')
    q.page['asr'] = cards.asr(recording=True)

    await q.page.save()


@on('stop')
async def stop_recording(q: Q):
    """
    Stop recording audio.
    """

    logging.info('Stopping recording')

    q.page['meta'].script = get_inline_script('stopRecording()')
    q.page['asr'] = cards.asr()

    await q.page.save()


@on('audio')
async def audio_inference(q: Q):
    """
    Running ASR inference on audio.
    """

    logging.info('Inferencing recorded audio')

    audio_path = await q.site.download(q.events.audio.captured, '.')

    q.client.transcription = generate_transcription(audio_path=audio_path, model=q.app.model, processor=q.app.processor)

    q.page['asr'] = cards.asr(audio_path=q.events.audio.captured, transcription=q.client.transcription)

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
