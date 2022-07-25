from h2o_wave import Q, main, app, handle_on

import handlers
from actions import show_error
from initializers import initialize_app, initialize_client


@app('/')
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """
    try:
        # Initialize the app if not already.
        await initialize_app(q)

        # Initialize the client (browser tab) if not already.
        await initialize_client(q)
        await handle_on(q)
    except Exception as error:
        await show_error(q, error=str(error))
