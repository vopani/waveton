import sys
import traceback

from h2o_wave import ui

import layouts

DROPPABLE_CARDS = [
    'home',
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
                    To report this issue, please open an 
                    <a href="https://github.com/vopani/waveton/issues/new?assignees=vopani&labels=bug&template=error-report.md&title=%5BERROR%5D" target="_blank">Issue on GitHub</a>
                    with the details below:</center>''',
                visible=False
            ),
            ui.text_l(content='Report Issue in App: **Theme Switch**', visible=False),
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
        title='Theme Switch',
        subtitle='Toggling between light and dark modes',
        icon='Color',
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
        caption='Learn more about <a href="https://github.com/vopani/waveton" target="_blank"> WaveTon: 💯 Wave Applications</a>'
    )

    return card


def home() -> ui.FormCard:
    """
    Card for home page.
    """

    card = ui.form_card(
        box='home',
        items=[
            ui.text('This is dark mode'),
            ui.text('''You can read more about creating custom themes using
                    <a href="https://wave.h2o.ai/docs/examples/theme-generator" target="_blank">Theme Generator</a>''')
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
