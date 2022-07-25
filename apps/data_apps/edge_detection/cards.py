import sys
import traceback

import pandas as pd

from h2o_wave import Q, ui, expando_to_dict

import layouts
from constants import EdgeDetectionKernels


# Link to repo. Report bugs/features here :)
issue_link = 'https://github.com/vopani/waveton/issues/new?assignees=vopani&labels=bug&template=error-report.md&title=%5BERROR%5D'


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


def header() -> ui.HeaderCard:
    """
    Card for header.
    """

    card = ui.header_card(
        box='header',
        title='Edge Detector',
        subtitle='Tool to visualize edge detection algorithms',
        icon='ImageSearch',
        icon_color='black',
        items=[
            ui.toggle(name='theme_dark', label='Dark Mode', value=True, trigger=True)
        ]
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


def command_panel(edge_detection_kernel, gaussian_blur, gaussian_kernel_size) -> ui.FormCard:
    """
    Card for control panel.
    """

    kernel_choices = [
        ui.choice(
            name=EdgeDetectionKernels.LAPLACE.value,
            label=EdgeDetectionKernels.LAPLACE.value
        ),
        ui.choice(
            name=EdgeDetectionKernels.SOBEL.value,
            label=EdgeDetectionKernels.SOBEL.value
        )
    ]

    return ui.form_card(
        box='commands',
        items=[
            ui.text_xl("Command Panel"),
            ui.file_upload(
                name="image_uploader",
                label="Upload",
                multiple=False,
                file_extensions=['jpeg', 'png'],
            ),
            ui.separator(),
            ui.text_xl("Kernel Configurations"),
            ui.choice_group(
                name="edge_detection_kernel",
                label="Select Kernel",
                choices=kernel_choices,
                value=edge_detection_kernel
            ),
            ui.separator(),
            ui.text_xl("Blur Configurations"),
            ui.checkbox(
                name="gaussian_blur",
                label="Apply Gaussian Blur for Smoothing",
                value=gaussian_blur,
            ),
            ui.text_xl("\n"),
            ui.slider(
                name="gaussian_kernel_size",
                label="Blur Kernel Size",
                min=3,
                max=21,
                step=2,
                value=gaussian_kernel_size
            ),
            ui.text_xl("\n"),
            ui.buttons(
                items=[
                    ui.button(
                        name="run_edge_detection",
                        label="Detect",
                        primary=True,
                        icon="Search"
                    )
                ]
            )

        ],
    )


def original_image_viewer(image_path) -> ui.ImageCard:
    """
    Card to display original image.
    """
    return ui.image_card(
        box='main_top_left',
        title="Original Image",
        path=image_path
    )


def processed_image_viewer(image_path) -> ui.ImageCard:
    """
    Card to display processed image.
    """
    return ui.image_card(
        box='main_top_right',
        title="Processed Image",
        path=image_path
    )


def image_table(image_df: pd.DataFrame) -> ui.FormCard:
    """
    Card to display uploaded image table.
    """
    columns = [
        ui.table_column(
            name="image_name",
            label="Image",
            sortable=True,
            searchable=True,
            link=True,
            max_width="750px"
        ),
        ui.table_column(
            name="uploaded_time",
            label="Uploaded At",
            sortable=True,
        )
    ]

    rows = [
        ui.table_row(
            name=row.Image,
            cells=[row.Image, row.Timestamp]
        ) for row in image_df.itertuples()
    ]

    table = ui.table(
        name="image_table",
        columns=columns,
        rows=rows,
        height='calc(((100vh - 150px)/3) - 75px)'
    )
    return ui.form_card(
        box='main_bottom',
        items=[
            table
        ]
    )
