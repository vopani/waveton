import sys
import traceback

import datatable as dt
from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'CSV Loader'

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
                ui.zone(name='main', direction='row', size='calc(100vh - 130px)'),
                ui.zone(name='footer')
            ]
        )
    ],
    theme='h2o-dark'
)

# The header shown on all the app's pages
header = ui.header_card(
    box='header',
    title='CSV Loader',
    subtitle='Load a csv file into a table',
    icon='Table',
    icon_color='black',
    items=[ui.toggle(name='theme_dark', label='Dark Mode', value=True, trigger=True)]
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


def upload(path_default_data: str) -> ui.FormCard:
    """
    Card for uploading data.
    """

    card = ui.form_card(
        box=ui.box(zone='main', order=1, size=1),
        items=[
            ui.text_l(content='<center>Upload a csv file'),
            ui.inline(
                items=[ui.file_upload(name='upload', file_extensions=['csv'], height='200px', max_file_size=100)],
                justify='center'
            ),
            ui.text(content=f'<center>Or use the sample file: <a href="{path_default_data}">waveton_sample.csv')
        ]
    )

    return card


def table(name: str, data: dt.Frame) -> ui.FormCard:
    """
    Card for displaying csv data in table.
    """

    card = ui.form_card(
        box=ui.box(zone='main', order=2, size=10),
        items=[
            ui.text_l(content=f'<center>{name}'),
            ui.table(
                name='data',
                columns=[ui.table_column(
                    name=str(col),
                    label=str(col),
                    sortable=True,
                    searchable=True,
                    filterable=True,
                    link=False
                ) for col in data.names],
                rows=[ui.table_row(
                    name=str(i),
                    cells=[str(value) for value in data[i, :].to_tuples()[0]]
                ) for i in range(data.nrows)],
                groupable=True,
                downloadable=True,
                resettable=True,
                height='calc(100vh - 210px)'
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
