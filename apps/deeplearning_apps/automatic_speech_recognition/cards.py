import sys
import traceback

from h2o_wave import Q, expando_to_dict, ui

# App name
app_name = 'Automatic Speech Recognition'

# Link to repo. Report bugs/features here :)
repo_url = 'https://github.com/vopani/waveton'
issue_url = f'{repo_url}/issues/new?assignees=vopani&labels=bug&template=error-report.md&title=%5BERROR%5D'

# JS scripts
encoder_url = 'https://cdn.jsdelivr.net/npm/opus-media-recorder@latest/encoderWorker.umd.js'
recorder_url = 'https://cdn.jsdelivr.net/npm/opus-media-recorder@latest/OpusMediaRecorder.umd.js'

with open('record.js', encoding='utf-8') as f:
    recorder_script = ui.inline_script(f.read())

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
    theme='h2o-dark',
    scripts=[
        ui.script(encoder_url, asynchronous=False),
        ui.script(recorder_url, asynchronous=False)
    ],
    script=recorder_script
)

# The header shown on all the app's pages
header = ui.header_card(
    box='header',
    title='Automatic Speech Recognition',
    subtitle='Speech to text in English',
    icon='Microphone',
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


def asr(recording: bool = False, audio_path: str = None, transcription: str = '') -> ui.FormCard:
    """
    Card for Automatic Speech Recognition.
    """

    button_name = 'stop' if recording else 'start'
    button_label = '⏹️ Stop Recording' if recording else '🎙️ Start Recording'
    visible = False if audio_path is None else True

    card = ui.form_card(
        box='main',
        items=[
            ui.separator(label='Microphone'),
            ui.buttons(items=[ui.button(name=button_name, label=button_label, primary=True)], justify='center'),
            ui.separator(label='Audio', visible=visible),
            ui.text(
                content=f'''<center>
                    <audio controls><source src="{audio_path}" type="audio/wav"></source></audio>
                    <center>''',
                visible=visible
            ),
            ui.separator(label='Transcription', visible=visible),
            ui.textbox(name='transcription', value=transcription, multiline=True, visible=visible)
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
