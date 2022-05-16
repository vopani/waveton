from h2o_wave import ui

def meta() -> ui.MetaCard:
    """
    Card for meta information.
    """

    card = ui.meta_card(
        box='',
        title='H2O Wave ML',
        redirect='#home',
        layouts=[
            layouts.small(),
            layouts.large()
        ],
        theme='neon'
    )

    return card
