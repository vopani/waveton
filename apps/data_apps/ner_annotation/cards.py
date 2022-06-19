import sys
import traceback

from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'NER Annotation'

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
                        ui.zone(name='ner_entities', size='20%'),
                        ui.zone(name='ner_annotator', size='80%')
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
    title='NER Annotation',
    subtitle='Annotate entities for Named-Entity Recognition tasks',
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

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)


def ner_entities(ner_tags: list[dict]) -> ui.FormCard:
    """
    Card for NER entities.
    """

    card = ui.form_card(
        box='ner_entities',
        items=[
            ui.textbox(name='new_entity_name', label='Type an entity to be added'),
            ui.buttons(
                items=[
                    ui.button(name='add', label='Add', primary=True)
                ],
                justify='center'
            ),
            ui.separator(),
            ui.dropdown(
                name='delete_entity_name',
                label='Select an entity to delete',
                choices=[ui.choice(name=tag['name'], label=tag['label']) for tag in ner_tags]
            ),
            ui.buttons(
                items=[
                    ui.button(name='delete', label='Delete', primary=True)
                ],
                justify='center'
            ),
        ]
    )

    return card


def ner_annotator(
    ner_tags: list[dict],
    ner_items: list[dict],
    disable_next: bool = False,
    disable_previous: bool = False
) -> ui.FormCard:
    """
    Card for NER annotator.
    """

    card = ui.form_card(
        box='ner_annotator',
        items=[
            ui.text_annotator(
                name='ner_annotator',
                title='Click and/or drag text to annotate',
                tags=[ui.text_annotator_tag(**tag) for tag in ner_tags],
                items=[ui.text_annotator_item(**item) for item in ner_items]
            ),
            ui.buttons(
                items=[
                    ui.button(name='next', label='Next', primary=True, disabled=disable_next),
                    ui.button(name='previous', label='Previous', disabled=disable_previous)
                ]
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
