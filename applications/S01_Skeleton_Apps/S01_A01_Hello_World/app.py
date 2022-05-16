import logging

from h2o_wave import Q, main, app, ui

logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)


@app('/')
async def serve(q: Q):
    """
    App function.
    """

    q.page['meta'] = ui.meta_card(
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

    q.page['header'] = ui.header_card(
        box='header',
        title='Hello World',
        subtitle='A simple example'
    )

    q.page['main'] = ui.form_card(
        box='main',
        items=[
            ui.text(content='Welcome to WaveTon!')
        ]
    )

    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='App 1 of [WaveTon: 💯 Wave Applications](https://github.com/vopani/waveton)'
    )

    await q.page.save()
