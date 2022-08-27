import sys
import traceback

from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'Stable Diffusion'

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
                ui.zone(name='main'),
                ui.zone(name='footer')
            ]
        )
    ],
    theme='h2o-dark'
)

# The header shown on all the app's pages
header = ui.header_card(
    box='header',
    title='Stable Diffusion',
    subtitle='Generate images from prompts using Stable Diffusion model',
    icon='PictureTile',
    icon_color='black',
    items=[
        ui.toggle(name='theme_dark', label='Dark Mode', value=True, trigger=True)
    ]
)

# The footer shown on all the app's pages
footer = ui.footer_card(
    box='footer',
    caption=f'Learn more about <a href="{repo_url}" target="_blank"> WaveTon: 💯 Wave Applications</a>'
)

# Card for GPU unavailability
gpu = ui.form_card(
    box='main',
    items=[
        ui.stats(
            items=[
                ui.stat(
                    label='',
                    value='Unable to locate GPU and/or CUDA',
                    caption='This application requires a GPU to run',
                    icon='Error',
                    icon_color='#FEC924'
                )
            ],
            justify='center'
        )
    ]
)

# Card for setting up HuggingFace access
setup = ui.form_card(
    box='main',
    items=[
        ui.textbox(name='access_token', label='HuggingFace Access Token', password=True),
        ui.buttons(
            items=[
                ui.button(name='save', label='Save', primary=True)
            ],
            justify='center'
        ),
        ui.text(content='''<center>
            📃 Please read and accept the model license on 
            <a href="https://huggingface.co/CompVis/stable-diffusion-v1-4" target="_blank">
            https://huggingface.co/CompVis/stable-diffusion-v1-4</a>
        </center>'''),
        ui.text(content='''<center>
            🔑 You can find your HuggingFace access token on 
            <a href="https://huggingface.co/settings/tokens" target="_blank">
            https://huggingface.co/settings/tokens</a>
        </center>''')
    ]
)

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)


def main(images: int, steps: int, guidance_scale: float, image_paths=None) -> ui.FormCard:
    """
    Card for entering prompt and displaying generated images.
    """

    card_items=[
        ui.textbox(name='prompt', label='Prompt'),
        ui.inline(
            items=[
                ui.slider(
                    name='images',
                    label='Images',
                    min=1,
                    max=5,
                    value=images,
                    width='400px'
                ),
                ui.slider(
                    name='steps',
                    label='Steps',
                    min=1,
                    max=50,
                    value=steps,
                    width='400px'),
                ui.slider(
                    name='guidance_scale',
                    label='Guidance Scale',
                    min=0.0,
                    max=50.0,
                    step=0.5,
                    value=guidance_scale,
                    width='400px')
            ],
            justify='around'
        ),
        ui.buttons(
            items=[
                ui.button(name='generate', label='Generate', primary=True)
            ],
            justify='center'
        ),
        ui.separator(label='')
    ]

    if image_paths is not None:
        card_items.extend([
            ui.inline(
                items=[
                    ui.image(
                        title=f'sd_image_{i}',
                        path=image_path,
                        width=f'{100/len(image_paths)}%'
                    ) for i, image_path in enumerate(image_paths)
                ],
                justify='center'
            )
        ])

    card = ui.form_card(
        box='main',
        items=card_items
    )
    
    return card


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
        box='main',
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
