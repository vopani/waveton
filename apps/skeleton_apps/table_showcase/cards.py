import sys
import traceback

from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'Table Showcase'

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
    title='Table Showcase',
    subtitle='Various features of using a table',
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

# Columns of table
table_columns = [
    ui.table_column(
        name='id',
        label='Id',
        min_width='20px'
    ),
    ui.table_column(
        name='user',
        label='User',
        sortable=True,
        filterable=True,
        searchable=True,
        min_width='100px'
    ),
    ui.table_column(
        name='product',
        label='Product',
        sortable=True,
        filterable=True,
        searchable=True,
        min_width='100px'
    ),
    ui.table_column(
        name='description',
        label='Description',
        cell_type=ui.markdown_table_cell_type(),
        searchable=True
    ),
    ui.table_column(
        name='icon',
        label='Icon',
        cell_type=ui.icon_table_cell_type(),
        min_width='30px'
    ),
    ui.table_column(
        name='picture',
        label='Picture',
        cell_type=ui.markdown_table_cell_type(),
        min_width='50px'
    ),
    ui.table_column(
        name='audio',
        label='Audio',
        cell_type=ui.markdown_table_cell_type(),
        min_width='300px'
    ),
    ui.table_column(
        name='quantity',
        label='Quantity',
        data_type='number',
        sortable=True,
        min_width='95px'
    ),
    ui.table_column(
        name='discount',
        label='Discount',
        cell_type=ui.progress_table_cell_type(),
        sortable=True,
        min_width='80px'
    ),
    ui.table_column(
        name='tags',
        label='Tags',
        cell_type=ui.tag_table_cell_type(
            name='',
            tags=[
                ui.tag(label='Beverage', color='$brown'),
                ui.tag(label='Home', color='$blue'),
                ui.tag(label='Retail', color='$purple'),
                ui.tag(label='Sale', color='$red')
            ]
        ),
        searchable=True
    ),
    ui.table_column(
        name='menu',
        label='Menu',
        cell_type=ui.menu_table_cell_type(
            commands=[
                ui.command(name='view_transaction', label='View Transaction', icon='Shop'),
                ui.command(name='view_image', label='View Image', icon='ImageSearch')
            ]
        ),
        min_width='40px'
    )
]

table_rows = [
    ui.table_row(
        name='0',
        cells=['0', 'Adam', 'Coffee',
               '<b>Product</b>: <i>Coffee</i>\n<b>Category</b>: <i>Beverages</i>', 'CoffeeScript',
               '<center><img src="https://images.unsplash.com/photo-1587049016823-69ef9d68bd44" width="70%">',
               '<center><audio controls><source src="https://media.merriam-webster.com/audio/prons/en/us/mp3/c/coffee01.mp3" type="audio/wav">',
               '1', '0.09', 'Beverage,Sale']
    ),
    ui.table_row(
        name='1',
        cells=['1', 'Sarah', 'Balloons',
               '<b>Product</b>: <i>Balloons</i>\n<b>Category</b>: <i>Home</i>', 'Balloons',
               '<center><img src="https://images.unsplash.com/photo-1574276254982-d209f79d673a" width="70%">',
               '<center><audio controls><source src="https://media.merriam-webster.com/audio/prons/en/us/mp3/b/balloo01.mp3" type="audio/wav">',
               '10', '0.66', 'Home,Sale']
    ),
    ui.table_row(
        name='2',
        cells=['2', 'Adam', 'Television',
               '<b>Product</b>: <i>Television</i>\n<b>Category</b>: <i>Retail</i>', 'TVMonitor',
               '<center><img src="https://images.unsplash.com/photo-1552975084-6e027cd345c2" width="70%">',
               '<center><audio controls><source src="https://media.merriam-webster.com/audio/prons/en/us/mp3/t/televi03.mp3" type="audio/wav">',
               '1', '0', 'Retail']
    ),
    ui.table_row(
        name='3',
        cells=['3', 'Jen', 'Balloons',
               f'<b>Product</b>: <i>Balloons</i>\n<b>Category</b>: <i>Home</i>', 'Balloons',
               '<center><img src="https://images.unsplash.com/photo-1574276254982-d209f79d673a" width="70%">',
               '<center><audio controls><source src="https://media.merriam-webster.com/audio/prons/en/us/mp3/b/balloo01.mp3" type="audio/wav">',
               '3', '0.15', 'Home,Sale']
    )
]


def table(pagination: bool = False) -> ui.FormCard:
    """
    Card for table.
    """

    pagination = ui.table_pagination(total_rows=4, rows_per_page=2) if pagination else None

    card = ui.form_card(
        box='main',
        items=[
            ui.table(
                name='transactions',
                columns=table_columns,
                rows=table_rows,
                pagination=pagination,
                groupable=True,
                resettable=True,
                downloadable=True,
                events=['page_change'],
                height='520px'
            ),
            ui.buttons(
                items=[
                    ui.button(
                        name='unpaginate' if pagination else 'paginate',
                        label='Unpaginate' if pagination else 'Paginate',
                        primary=True
                    ),
                    ui.button(name='multiselect', label='Multiselect', primary=True)
                ],
                justify='center'
            )
        ]
    )

    return card


def update_table_rows(page_offset: int = 0) -> list[ui.TableRow]:
    """
    Update rows of table.
    """

    return table_rows[page_offset: page_offset + 2]


def dialog_transaction(rows: list[int]) -> ui.Dialog:
    """
    Dialog for viewing transaction.
    """

    if len(rows) == 1:
        if rows[0] == 0:
            user, product, category, quantity = 'Adam', 'Coffee', 'Beverage', 1
        elif rows[0] == 1:
            user, product, category, quantity = 'Sarah', 'Balloons', 'Home', 10
        elif rows[0] == 2:
            user, product, category, quantity = 'Adam', 'Television', 'Retail', 1
        else:
            user, product, category, quantity = 'Jen', 'Balloons', 'Home', 3

        items = [
            ui.text(f'**User**: {user}'),
            ui.text(f'**Product**: {product}'),
            ui.text(f'**Category**: {category}'),
            ui.text(f'**Quantity**: {quantity}'),
        ]
    else:
        items = []
        for row in rows:
            if row == 0:
                user, product, category, quantity = 'Adam', 'Coffee', 'Beverage', 1
            elif row == 1:
                user, product, category, quantity = 'Sarah', 'Balloons', 'Home', 10
            elif row == 2:
                user, product, category, quantity = 'Adam', 'Television', 'Retail', 1
            else:
                user, product, category, quantity = 'Jen', 'Balloons', 'Home', 3

            items.append(
                ui.text(f'**User**: {user}\t**Product**:{product}\t**Category**:{category}\t**Quantity**:{quantity}')
            )

    dialog = ui.dialog(
        name='dialog_transaction',
        title='Transaction(s)',
        items=items,
        closable=True,
        events=['dismissed']
    )

    return dialog


def dialog_image(row: int) -> ui.Dialog:
    """
    Dialog for viewing image.
    """

    if row == 0:
        image_path = 'https://images.unsplash.com/photo-1587049016823-69ef9d68bd44'
    elif row == 2:
        image_path = 'https://images.unsplash.com/photo-1552975084-6e027cd345c2'
    else:
        image_path = 'https://images.unsplash.com/photo-1574276254982-d209f79d673a'

    dialog = ui.dialog(
        name='dialog_image',
        title='Image',
        items=[ui.image(title='Image', path=image_path, width='100%')],
        closable=True,
        events=['dismissed']
    )

    return dialog


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
