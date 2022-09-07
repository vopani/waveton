import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'Image Augmentation Visualization'

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
                ui.zone(
                    name='main',
                    size='calc(100vh - 150px)',
                    direction='row',
                    zones=[
                        ui.zone(name='options_card', size='20%'),
                        ui.zone(name='image_card', size='40%'),
                        ui.zone(name='aug_image_card', size='40%'),

                    ]
                ),
                ui.zone(name='footer')
            ]
        )
    ],
    theme='h2o-dark'
)

# The header shown on all the app's pages
header = ui.header_card(
    box='header',
    title='Image Augmentation ',
    subtitle='Visualize augmented images for computer vision tasks',
    icon='Handwriting',
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

# Dialog for uploading new image
dialog_new_image = ui.dialog(
    name='dialog_new_image',
    title='Upload New Image',
    items=[ui.file_upload(name='upload', file_extensions=['jpg', 'jpeg', 'png'])],
    closable=True,
    events=['dismissed']
)

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)

# Dialog for uploading new image
dialog_new_image = ui.dialog(
    name='dialog_new_image',
    title='Upload New Image',
    items=[ui.file_upload(name='upload', file_extensions=['jpg', 'jpeg', 'png'])],
    closable=True,
    events=['dismissed']
)


def options_card(augs_type_list,prompt,dropdown_name) -> ui.FormCard:
    """
    Card for all augmentations option.
    """
    card = ui.form_card(
        box='options_card',

        items=[

            ui.dropdown(
                name='select_new_aug',
                label=prompt,
                choices=[ui.choice(name=tag, label=tag) for tag in augs_type_list]
            ),


            ui.buttons(
                items=[
                    ui.button(name=dropdown_name, label='Select', primary=True)
                ],
                justify='center'
            ),

            ui.separator(width="100%", visible=True),

            ui.buttons(
                items=[
                    ui.button(name='reset_aug_button', label='Reset Augmentations', primary=True)
                ],
                justify='center'
            ),
            ui.separator(width="100%", visible=True),

            # ui.textbox(name='resize_image_ratio', label='New Image Size Ratio [Float]'),
            ui.slider(name='resize_image_ratio', label='New Image Size', min=64, max=720),

            ui.buttons(
                items=[
                    ui.button(name='resize_images', label='Resize Images', primary=True)
                ],
                justify='center'
            ),
            ui.separator(label='New Image'),
            ui.buttons(
                items=[
                    ui.button(name='new_image', label='Add New', primary=True)
                ],
                justify='center'
            )
        ]
    )
    return card



def image_card(width_value, path):
    card = ui.form_card(
        box='image_card',
        items=[
            ui.label(label='Original Image'),

            ui.image(
                title='Original image',
                path=path,
                type='jpg', width=f"{width_value}px")
        ]

    )

    return card


def aug_image_card(width_value, path):
    card = ui.form_card(
        box='aug_image_card',
        items=[
            ui.label(label='Augmented Image', width="100%"),

            ui.image(
                title='Augmented image',
                path=path,
                type='jpg', width=f"{width_value}px"
            )
        ]

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
