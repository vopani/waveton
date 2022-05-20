from h2o_wave import ui

'''
-------------------------------------------------------------------------------
header
-------------------------------------------------------------------------------
 commands   |                           main
    20      |                            80
            |                               
            |
            |                                    
            |
            |                      
            |                              
            |                        
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
                direction='row',
                zones=[
                    ui.zone(name='commands', size='20%'),
                    ui.zone(name='main', size='80%')
                ]
            ),
            ui.zone(name='error'),
            ui.zone(name='footer')
        ]
    )

    return layout
