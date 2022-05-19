import sys
import traceback

from h2o_wave import ui

import layouts

DROPPABLE_CARDS = [
    'ner_tags',
    'ner_text',
    'error'
]


def meta() -> ui.MetaCard:
    """
    Card for meta information.
    """

    card = ui.meta_card(
        box='',
        title='WaveTon',
        layouts=[
            layouts.default()
        ],
        theme='h2o-dark'
    )

    return card


def error(q_app: dict, q_user: dict, q_client: dict, q_events: dict, q_args: dict) -> ui.FormCard:
    """
    Card for handling crash.
    """

    q_app_str = '### q.app\n```' + '\n'.join([f'{k}: {v}' for k, v in q_app.items()]) + '\n```'
    q_user_str = '### q.user\n```' + '\n'.join([f'{k}: {v}' for k, v in q_user.items()]) + '\n```'
    q_client_str = '### q.client\n```' + '\n'.join([f'{k}: {v}' for k, v in q_client.items()]) + '\n```'
    q_events_str = '### q.events\n```' + '\n'.join([f'{k}: {v}' for k, v in q_events.items()]) + '\n```'
    q_args_str = '### q.args\n```' + '\n'.join([f'{k}: {v}' for k, v in q_args.items()]) + '\n```'

    type_, value_, traceback_ = sys.exc_info()
    stack_trace = traceback.format_exception(type_, value_, traceback_)
    stack_trace_str = '### stacktrace\n' + '\n'.join(stack_trace)

    card = ui.form_card(
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
                justify='center'
            ),
            ui.separator(),
            ui.text_l(content='<center>Apologies for the inconvenience!</center>'),
            ui.buttons(
                items=[
                    ui.button(name='restart', label='Restart', primary=True),
                    ui.button(name='report', label='Report', primary=True)
                ],
                justify='center'
            ),
            ui.separator(visible=False),
            ui.text(
                content='''<center>
                    To report this issue, please open an issue on 
                    <a href="https://github.com/vopani/waveton/issues/new" target="_blank">https://github.com/vopani/waveton/issues/new</a>
                    with the details below:</center>''',
                visible=False
            ),
            ui.text_l(content='Report Issue in App: **NER Annotation**', visible=False),
            ui.text(content=q_app_str, visible=False),
            ui.text(content=q_user_str, visible=False),
            ui.text(content=q_client_str, visible=False),
            ui.text(content=q_events_str, visible=False),
            ui.text(content=q_args_str, visible=False),
            ui.text(content=stack_trace_str, visible=False)
        ]
    )

    return card


def header() -> ui.HeaderCard:
    """
    Card for header.
    """

    card = ui.header_card(
        box='header',
        title='NER Annotation',
        subtitle='Annotate entities for Named-Entity Recognition tasks',
        icon='Handwriting',
        icon_color='black',
        items=[ui.toggle(name='theme_dark', label='Dark Mode', value=True, trigger=True)]
    )

    return card


def footer() -> ui.FooterCard:
    """
    Card for footer.
    """

    card = ui.footer_card(
        box='footer',
        caption='Learn more about <a href="https://github.com/vopani/waveton" target="_blank">WaveTon: 💯 Wave Applications</a>'
    )

    return card


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
                choices=[ui.choice(name=tag['name'], label=tag['label']) for tag in ner_tags],
                value=ner_tags[0]['name']
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


def ner_annotator(ner_tags: list[dict], ner_items: list[dict]) -> ui.FormCard:
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
                    ui.button(name='next', label='Next', primary=True),
                    ui.button(name='previous', label='Previous')
                ]
            )
        ]
    )

    return card


def dummy() -> ui.FormCard:
    """
    Card for dummy use.
    """

    card = ui.form_card(
        box='dummy',
        items=[]
    )

    return card
