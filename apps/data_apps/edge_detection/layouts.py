from h2o_wave import ui

'''
-------------------------------------------------------------------------------
header
-------------------------------------------------------------------------------
 commands   |                         main_top
    20      |                            80
            |                            |  
            |                            |
            |        main_top_left 40    |           main_top_right 40     
            |                            |  
            |                            |
            |------------------------------------------------------------------                              
            |                        main_bottom
            |                        
            |                                
            |                                 
            |                                
            |
-------------------------------------------------------------------------------
error                                
-------------------------------------------------------------------------------
footer
-------------------------------------------------------------------------------
'''


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
                direction=ui.ZoneDirection.ROW,
                zones=[
                    ui.zone(name='commands', size='20%'),
                    ui.zone(
                        name='main',
                        size='80%',
                        direction=ui.ZoneDirection.COLUMN,
                        zones=[
                            ui.zone(
                                name="main_top",
                                size="70%",
                                direction=ui.ZoneDirection.ROW,
                                zones=[
                                    ui.zone(name="main_top_left", size="50%", direction=ui.ZoneDirection.ROW),
                                    ui.zone(name="main_top_right", size="50%", direction=ui.ZoneDirection.ROW)
                                ]
                            ),
                            ui.zone(name="main_bottom", size="30%")
                        ]
                    )
                ]
            ),
            ui.zone(name='error'),
            ui.zone(name='footer')
        ]
    )

    return layout
