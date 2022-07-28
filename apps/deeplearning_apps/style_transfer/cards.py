import sys
import traceback
from html_content import html
from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'Style Transfer App'

# Link to repo. Report bugs/features here :)
repo_url = 'https://github.com/vopani/waveton'
issue_url = f'{repo_url}/issues/new?assignees=vopani&labels=bug&template=error-report.md&title=%5BERROR%5D'

# A meta card to hold the app's title, layouts, dialogs, theme and other meta information
meta = ui.meta_card(
    box='',
    title='WaveTon',
    layouts=[
        ui.layout(
            breakpoint='xs',
            zones=[
                ui.zone(name='header'),
                ui.zone(name='main',direction='row',size='800px',),
                ui.zone(name='error'),
                ui.zone(name='footer')
            ]
        )
    ],
    theme='h2o-dark'
)

# The header shown on all the app's pages
header = ui.header_card(
    box='header',
    title='Style Transfer App',
    subtitle='A simple app to style images',
    icon='BuildQueue',
    icon_color='black'
)

# The footer shown on all the app's pages
footer = ui.footer_card(
    box='footer',
    caption=f'Learn more about <a href="{repo_url}" target="_blank"> WaveTon: 💯 Wave Applications</a>'
)

# Additional cards for the app's pages
main = ui.form_card(
    box='main',
    items=[
        ui.text('This is a great starting point to build an app.')
    ]
)

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)

def create_choice_list(items):
    return [ui.choice(name=k, label=k) for k in items]

async def create_dashboard(q,models_choice, source_image_choice):
    models = create_choice_list(models_choice)
    sources = create_choice_list(source_image_choice)
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
    return cfg

async def render_template(q: Q, page_cfg):
    q.page['main_left'] = ui.form_card(box=ui.box(
        zone='main', width='20%', order=1), title='', items=page_cfg['image_form'])
    q.page['main_right'] = ui.frame_card(box=ui.box(
            zone='main', width='80%', order=2), title='', content=page_cfg['image_slider_html'])
    await q.page.save()

def crash_report(q: Q) -> ui.FormCard:
    """
    Card for capturing the stack trace and current application state, for error reporting.
    This function is called by the main serve() loop on uncaught exceptions.
    """

    def code_block(content): return '\n'.join(['```', *content, '```'])

    type_, value_, traceback_ = sys.exc_info()
    stack_trace = traceback.format_exception(type_, value_, traceback_)

    dump = [
        '### Stack Trace',
        code_block(stack_trace),
    ]

    states = [
        ('q.app', q.app),
        ('q.user', q.user),
        ('q.client', q.client),
        ('q.events', q.events),
        ('q.args', q.args)
    ]
    for name, source in states:
        dump.append(f'### {name}')
        dump.append(code_block([f'{k}: {v}' for k, v in expando_to_dict(source).items()]))

    return ui.form_card(
        box='error',
        items=[
            ui.stats(
                items=[
                    ui.stat(
                        label='',
                        value='Oops!',
                        caption='Something went wrong',
                        icon='Error'
                    )
                ],
            ),
            ui.separator(),
            ui.text_l(content='Apologies for the inconvenience!'),
            ui.buttons(items=[ui.button(name='reload', label='Reload', primary=True)]),
            ui.expander(name='report', label='Error Details', items=[
                ui.text(
                    f'To report this issue, <a href="{issue_url}" target="_blank">please open an issue</a> with the details below:'),
                ui.text_l(content=f'Report Issue in App: **{app_name}**'),
                ui.text(content='\n'.join(dump)),
            ])
        ]
    )
