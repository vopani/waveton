import logging

from h2o_wave import Q, main, app, ui

logging.basicConfig(format='%(levelname)s:\t[%(asctime)s]\t%(message)s', level=logging.INFO)


@app('/')
async def serve(q: Q):
    """
    App function.
    """

    logging.info('Initializing the app')

    # A meta card to hold the app's title, layouts, dialogs, theme and other meta information
    q.page['meta'] = ui.meta_card(
        box='',
        title='WaveTon',
        layouts=[
            ui.layout(
                breakpoint='xs',
                zones=[
                    ui.zone(name='header'),
                    ui.zone(name='home'),
                    ui.zone(name='footer')
                ]
            )
        ],
        theme='h2o-dark'
    )

    # The header shown on all the app's pages
    q.page['header'] = ui.header_card(
        box='header',
        title='Hello Wave',
        subtitle='Hello World example',
        icon='WavingHand',
        icon_color='black'
    )

    # The main card of the app
    q.page['main'] = ui.form_card(
        box='main',
        items=[
            ui.text(content='Welcome to WaveTon!')
        ]
    )

    # The footer shown on all the app's pages
    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Learn more about <a href="https://github.com/vopani/waveton" target="_blank"> WaveTon: 💯 Wave Applications</a>'
    )

    # Save the page
    await q.page.save()
