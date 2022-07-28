from h2o_wave import Q, main, app, handle_on, expando_to_dict, Expando

import handlers
from actions import show_error
from initializers import initialize_app, initialize_client


@app('/')
async def serve(q: Q):
    """
    Main entry point. All queries pass through this function.
    """
    try:
        print_args(q)
        # Initialize the app if not already.
        await initialize_app(q)

        # Initialize the client (browser tab) if not already.
        await initialize_client(q)

        await handle_on(q)

        await q.page.save()
    except Exception as error:
        await show_error(q, error=str(error))


def print_args(q: Q):
    arg_dict = expando_to_dict(q.args)
    dict_to_print = dict()
    for key, value in arg_dict.items():
        if ('access_token' in key) or ('password' in key):
            continue
        dict_to_print[key] = value
    print(Expando(dict_to_print))
