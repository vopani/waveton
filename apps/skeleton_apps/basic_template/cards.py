import sys
import traceback

from h2o_wave import ui, Q, expando_to_dict

# Link to repo. Report bugs/features here :)
issue_link = 'https://github.com/vopani/waveton/issues/new?assignees=vopani&labels=bug&template=error-report.md&title=%5BERROR%5D'

# A meta card to hold our app's layouts
meta = ui.meta_card(
    box='',
    title='WaveTon',
    layouts=[
        ui.layout(
            breakpoint='xs',
            zones=[
                ui.zone(name='header'),
                ui.zone(name='home'),
                ui.zone(name='error'),
                ui.zone(name='footer')
            ]
        )
    ],
    theme='h2o-dark'
)

# The header shown on all our app's pages.
header = ui.header_card(
    box='header',
    title='Basic Template',
    subtitle='Building blocks to kickstart an app',
    icon='BuildQueue',
    icon_color='black'
)

# The footer shown on all our app's pages.
footer = ui.footer_card(
    box='footer',
    caption='Learn more about <a href="https://github.com/vopani/waveton" target="_blank"> WaveTon: 💯 Wave Applications</a>'
)


def create_crash_report(q: Q) -> ui.FormCard:
    """
    Creates a card that captures the stack trace and current application state, for error reporting.
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
        ('q.args', q.args),
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
                    f'To report this issue, <a href="{issue_link}" target="_blank">please open an issue</a> with the details below:'),
                ui.text_l(content='Report Issue in App: **Basic Template**'),
                ui.text(content='\n'.join(dump)),
            ]),
        ]
    )
