import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'Image Annotation'

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
                        ui.zone(name='image_classes', size='20%'),
                        ui.zone(name='image_annotator', size='80%'),
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
    title='Image Annotation ',
    subtitle='Annotate images for computer vision tasks',
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


def image_classes(image_tags: list[dict], image_height: int) -> ui.FormCard:
    """
    Card for image classes.
    """

    card = ui.form_card(
        box='image_classes',
        items=[
            ui.separator(label='Classes'),
            ui.textbox(name='new_class_name', label='Type a new class to be added'),
            ui.buttons(
                items=[
                    ui.button(name='add', label='Add', primary=True)
                ],
                justify='center'
            ),
            ui.dropdown(
                name='delete_class_name',
                label='Select a class to delete',
                choices=[ui.choice(name=tag['name'], label=tag['label']) for tag in image_tags]
            ),
            ui.buttons(
                items=[
                    ui.button(name='delete', label='Delete', primary=True)
                ],
                justify='center'
            ),
            ui.separator(label='Size'),
            ui.textbox(
                name='resize_height',
                label='Resize Image',
                placeholder=str(image_height),
                suffix='px',
                trigger=True
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


def image_annotator(
    image_path: str,
    image_tags: list[dict],
    image_items: list[dict] = None,
    image_height: int = None
) -> ui.FormCard:
    """
    Card for Image Annotator.
    """

    card = ui.form_card(
        box='image_annotator',
        items=[
            ui.image_annotator(
                name='image_annotator',
                title='Create boxes to annotate',
                image=image_path,
                tags=[ui.image_annotator_tag(**tag) for tag in image_tags],
                items=[ui.image_annotator_item(
                    shape=ui.image_annotator_rect(
                        x1=item['shape']['rect']['x1'],
                        y1=item['shape']['rect']['y1'],
                        x2=item['shape']['rect']['x2'],
                        y2=item['shape']['rect']['y2']
                    ),
                    tag=item['tag']
                ) for item in image_items] if image_items is not None else None,
                image_height=f'{image_height}px' if image_height is not None else None
            ),
            ui.buttons(
                items=[
                    ui.button(name='download', label='Download', primary=True)
                ],
                justify='center'
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
