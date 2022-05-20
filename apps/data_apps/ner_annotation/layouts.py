from h2o_wave import ui


def default() -> ui.Layout:
    """
    Layout for any screen size.
    """

    layout = ui.layout(
        breakpoint='xs',
        zones=[
            ui.zone(name='header'),
            ui.zone(
                name='home',
                size='calc(100vh - 150px)',
                direction='row',
                zones=[
                    ui.zone(name='ner_entities', size='20%'),
                    ui.zone(name='ner_annotator', size='80%')
                ]
            ),
            ui.zone(name='error'),
            ui.zone(name='footer')
        ]
    )

    return layout
