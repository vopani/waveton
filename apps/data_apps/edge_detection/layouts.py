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
        max_height='calc(100vh)',
        zones=[
            ui.zone(name='header',),
            ui.zone(
                name='home',
                size='calc(100vh - 125px)',
                direction=ui.ZoneDirection.COLUMN,
                zones=[
                    ui.zone(
                        name='commands',
                        direction=ui.ZoneDirection.ROW,
                    ),
                    ui.zone(
                        name='main',
                        direction=ui.ZoneDirection.COLUMN,
                        zones=[
                            ui.zone(
                                name="main_top",
                                direction=ui.ZoneDirection.ROW,
                                size="calc(100vh - 300px)",
                                zones=[
                                    ui.zone(name="main_top_left", size="50%", direction=ui.ZoneDirection.COLUMN),
                                    ui.zone(name="main_top_right", size="50%", direction=ui.ZoneDirection.COLUMN)
                                ]
                            ),
                            ui.zone(
                                name="main_bottom",
                                direction=ui.ZoneDirection.ROW,
                                zones=[
                                    ui.zone(name="main_bottom_left", size="50%", direction=ui.ZoneDirection.ROW,),
                                    ui.zone(name="main_bottom_right", size="50%", direction=ui.ZoneDirection.ROW,)
                                ]
                            )
                        ]
                    )
                ]
            ),
            ui.zone(name='error'),
            ui.zone(name='footer')
        ]
    )

    return layout
