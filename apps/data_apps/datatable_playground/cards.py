import sys
import traceback

from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'Datatable Playground'

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
                ui.zone(name='main', size='calc(100vh - 130px)'),
                ui.zone(name='footer')
            ]
        )
    ],
    theme='h2o-dark'
)

# The header shown on all the app's pages
header = ui.header_card(
    box='header',
    title='Datatable Playground',
    subtitle='Explore Python Datatable with tabular datasets',
    icon='TableComputed',
    icon_color='black',
    items=[ui.toggle(name='theme_dark', label='Dark Mode', value=True, trigger=True)]
)

# The footer shown on all the app's pages
footer = ui.footer_card(
    box='footer',
    caption=f'Learn more about <a href="{repo_url}" target="_blank"> WaveTon: 💯 Wave Applications</a>'
)

# Card for displaying query and table
main = ui.form_card(
    box='main',
    items=[
        ui.inline(
            items=[
                ui.textbox(
                    name='query',
                    label='Dataset Query',
                    placeholder='eg: data[dt.f.price > 1, :]',
                    value='',
                    spellcheck=False,
                    trigger=True,
                    tooltip='Refer the dataset using "data", "df" or "DT", & datatable as "dt"',
                    width='80%',
                ),
                ui.dropdown(
                    name='dataset',
                    label='Select Dataset',
                    choices=[ui.choice(name='waveton_sample.csv', label='waveton_sample.csv')],
                    value='waveton_sample.csv',
                    trigger=True,
                    width='15%'
                )
            ]
        ),
        ui.separator(label=''),
        ui.table(name='data', columns=[], height='calc(100vh - 285px)')
    ],
    commands=[ui.command(name='add_dataset', label='Add New Dataset', icon='Upload')]
)

# Dialog for adding new dataset
dialog_upload_dataset = ui.dialog(
    name='dialog_upload_dataset',
    title='Upload New Dataset',
    items=[ui.file_upload(name='upload', file_extensions=['csv', 'jay', 'txt', 'xlsx'])],
    closable=True,
    events=['dismissed']
)

# A fallback card for handling bugs
fallback = ui.form_card(
    box='fallback',
    items=[ui.text('Uh-oh, something went wrong!')]
)


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
