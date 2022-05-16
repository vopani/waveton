from h2o_wave import ui


def default() -> ui.Layout:
    """
    Layout for any screen size.
    """

    layout = ui.layout(
        breakpoint='xs',
        zones=[
            ui.zone(name='header'),
            ui.zone(name='home'),
            ui.zone(name='error'),
            ui.zone(name='footer')
        ]
    )

    return layout
