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
                        ui.zone(name='main2',size='75%', direction='column',
                                zones=[ui.zone(name='image_with_options_card', size='45%', direction='row',
                                               zones=[ui.zone(name='image_card', size='60%'),
                                                      ui.zone(name='extra_img_options_card', size='40%')]
                                                      ),
                                       ui.zone(name='aug_image_card', size='45%'),
                                       ui.zone(name='main3',size='10%',direction='row',
                                               zones = [ui.zone(name='current_light_augs_buttons_card',size='50%'),
                                                        ui.zone(name='current_hard_augs_buttons_card',size='50%'),
                                                        ])])

                    ]
                ),
                ui.zone(name='footer')
            ]
        )],
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


def options_card(light_augs_list,hard_augs_list) -> ui.FormCard:
    """
    Card for all augmentations option.
    """
    card = ui.form_card(
        box='options_card',

        items=[

            ui.dropdown(
                name='select_light_aug',
                label='Select The Light Augmentation',
                choices=[ui.choice(name=tag, label=tag) for tag in light_augs_list]
            ),
            ui.expander(name='expander', label='Adjust Parameters', items=[
                ui.slider(name='slider_p_value_light', label='Select Prob Of Augmentation', min=0, max=1,step=0.1,value=1.0),
            ]),

            ui.buttons(
                items=[
                    ui.button(name='select_light_aug_button', label='Select', primary=True)
                ],
                justify='center'
            ),

            ui.separator(width="100%", visible=True),

            ui.dropdown(
                name='select_hard_aug',
                label='Select The Hard Augmentation',
                choices=[ui.choice(name=tag, label=tag) for tag in hard_augs_list]
            ),

            ui.expander(name='expander2', label='Adjust Parameters', items=[
                ui.slider(name='slider_p_value_hard', label='Select Prob Of Augmentation', min=0, max=1, step=0.1,
                          value=1.0),
            ]),
            ui.buttons(
                items=[
                    ui.button(name='select_hard_aug_button', label='Select', primary=True)
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
            ui.separator(label='New Image',width="100%", visible=True),

            ui.buttons(
                items=[
                    ui.button(name='new_image', label='Add New', primary=True)
                ],
                justify='center'
            )

        ]
    )
    return card


def current_light_augs_buttons_card(selected_light_augs_names) -> ui.FormCard:

    card = ui.form_card(
        box='current_light_augs_buttons_card',
        items=[ui.text_l('Selected Light Augmentations'),
            ui.buttons(
            items=[
                ui.button(name=name, label=name, primary=True) for name in selected_light_augs_names],
                      ),
    ])

    return card

def current_hard_augs_buttons_card(selected_hard_augs_names) -> ui.FormCard:

    card = ui.form_card(
        box='current_hard_augs_buttons_card',
        items=[
            ui.text_l('Selected Hard Augmentations'),
            ui.buttons(
            items=[
                ui.button(name=name, label=name, primary=True) for name in selected_hard_augs_names],
                    )
    ])

    return card


def extra_img_options_card() -> ui.FormCard:
    card = ui.form_card(
        box='extra_img_options_card',
        items=[
            ui.slider(name='resize_image_ratio', label='Select Image Size', min=64, max=720),
            ui.buttons(
                items=[
                    ui.button(name='resize_images', label='Resize Images', primary=True)
                ],
                justify='center'
            ),

            ui.slider(name='num_aug_images', label='Number of Augmented Images ', min=2, max=8),
            ui.buttons(
                items=[
                    ui.button(name='num_aug_images_button', label='Select Images', primary=True)
                ],
                justify='center'
            ),

        ])
    return card

def image_card(width_value, path):
    card = ui.form_card(
        box='image_card',
        items=[
            ui.label(label='Original Image'),
            ui.image(
                title='Original image',
                path=path,
                type='jpg', width=f"{width_value}px"),

        ]
    )

    return card


def aug_image_card(width_value, paths):
    card = ui.form_card(
        box='aug_image_card',
        items=[
            ui.label(label='Augmented Images', width="100%"),

            ui.inline(
            [ui.image(
                title='Augmented image',
                path=path,
                type='jpg', width=f"{width_value}px"
            ) for path in paths]),
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
