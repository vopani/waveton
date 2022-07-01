from html_content import html
import logging

from h2o_wave import Q, main, app, handle_on, on, ui
from constants import * 
import os

import cards
from style import load_model, stylize

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
            q.app.initialized = True  # Mark as initialized at the app level (global to all clients)

        # Initialize the client (browser tab) if not already
        if not q.client.initialized:
            await initialize_client(q)
            q.client.initialized = True  # Mark as initialized at the client (browser tab) level

        if q.args.source_img is not None:
            q.user.source_img = q.args.source_img
            img = q.args.source_img
            q.user.input_image = "static/" + img
            q.user.output_image = "static/" + img
            q.args.tabs = 'dashboard_tab'
        else:
            img = source_image_choice[0]
            q.user.input_image = "static/" + img
        
        if q.args.style_model is not None:
            q.user.style_model = q.args.style_model
            q.user.template_image_path, = await q.site.upload(['static/'+q.user.style_model+'.jpg'])
            q.args.tabs = 'dashboard_tab'
        
        if len(os.listdir('generated')) > 5:
            for i in os.listdir('generated'):
                os.remove('generated/'+i)


        if q.args.try_your_image:
            q.user.apply_style = False
            if q.user.try_your_image is True:
                q.user.try_your_image = False
            else:
                q.user.try_your_image = True
            q.args.tabs = 'dashboard_tab'

        
        if q.args.apply_style:
            if q.user.try_your_image is True:
                try:
                    local_path = await q.site.download(q.args.upload_image[0], 'input/'+q.args.upload_image[0].split('/')[-1].replace(' ','_'))
                    q.user.input_image = input_image = 'input/' + os.path.basename(local_path)
                except:
                    q.user.input_image = input_image = "static/" + img
            else:
                q.user.input_image = input_image = "static/" + img
            style_name = q.args.style_model

            model = "saved_models/" + style_name + ".pth"
            q.user.output_image = output_image = "generated/" + style_name + "-" + img
            model = load_model(model)     
            stylize(model, input_image, output_image)
            q.user.style_name = q.args.style_model
            q.user.apply_style = q.args.apply_style
            q.args.tabs = 'dashboard_tab'
        if q.user.apply_style:
            q.args.tabs = 'dashboard_tab'
            # Delegate query to query handlers
        if q.args.tabs == 'dashboard_tab':
            await dashboard_page(q, {})
        elif await handle_on(q):
            pass
        
        # This condition should never execute unless there is a bug in our code
        # Adding this condition here helps us identify those cases (instead of seeing a blank page in the browser)
        else:
            await handle_fallback(q)

    except Exception as error:
        await show_error(q, error=str(error))

async def dashboard_page(q, details=None):
	models = [ui.choice(name=i, label=i)
            for i in models_choice]
	sources = [ui.choice(name=i, label=i)
            for i in source_image_choice]
	image_form = [ui.button(name='try_your_image', label='Try Existing Image' if q.user.try_your_image else 'Try Your Image')]
	if q.user.try_your_image:
		image_form = image_form + [ui.file_upload(
            name='upload_image', label='Upload your image', compact=True),]
	else:
		image_form = image_form + [
			ui.dropdown(trigger = True, popup='always', name = 'source_img', label = 'Source Image', value =q.args.source_img or source_image_choice[0], choices=sources),
		]
	image_form = image_form + [
		ui.dropdown(trigger = True, name='style_model', label='Style Model',
		            value=q.args.style_model or models_choice[0], choices=models),
        ui.button(name='apply_style', label="Apply Style"),
        ui.expander(name='preview', expanded=True, label='Style Preview', items=[
			ui.text("<img src='"+ q.user.template_image_path+"' width='99%' >")
		]),
	]
	# BASE_URL = 'https://mystique-transfer-learning.herokuapp.com'
	BASE_URL = 'http://localhost:10101'
	local_path_color, = await q.site.upload([q.user.input_image])
	local_path_bw, = await q.site.upload([q.user.output_image if q.user.apply_style else q.user.input_image])
	image_slider_html = html

	image_slider_html = image_slider_html.format(
		color=BASE_URL + local_path_color, bw=BASE_URL + local_path_bw)


	cfg = {
            'tag': 'dashboard',
			'image_form': image_form,
			'image_slider_html': image_slider_html
    }
	await render_template(q, cfg)
	
async def render_template(q: Q, page_cfg):
    q.page['main_left'] = ui.form_card(box=ui.box(
        zone='main', width='20%', order=1), title='', items=page_cfg['image_form'])
    q.page['main_right'] = ui.frame_card(box=ui.box(
            zone='main', width='80%', order=2), title='', content=page_cfg['image_slider_html'])
    await q.page.save()


async def initialize_app(q: Q):
    """
    Initialize the app.
    """

    logging.info('Initializing app')

    # Add app-level initialization logic here (loading datasets, database connections, etc.)
    q.app.cards = ['main']


async def initialize_client(q: Q):
    """
    Initialize the client (browser tab).
    """

    logging.info('Initializing client')
    img = source_image_choice[0]
    q.user.input_image = "static/" + img
    q.user.style_model = 'candy'
    q.user.template_image_path, = await q.site.upload(['static/candy.jpg'])
    q.page['meta'] = cards.meta
    q.page['header'] = cards.header
    q.page['footer'] = cards.footer
    await dashboard_page(q,{})


def clear_cards(q: Q, card_names: list):
    """
    Clear cards from the page.
    """

    logging.info('Clearing cards')

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
