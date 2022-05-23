from h2o_wave import Q, main, app, handle_on, expando_to_dict

import handlers
from actions import handle_error
from initializers import initialize_app, initialize_client
from constants import DEFAULT_LOGGER


@app('/')
async def serve(q: Q):
    """
    App function.
    """
    print_q_args(q.args)

    try:
        await initialize_app(q)
        await initialize_client(q)
        await handle_on(q)

    except Exception as error:
        await handle_error(q, error=str(error))


def print_q_args(q_args):
    DEFAULT_LOGGER.debug('>>>> q.args >>>>')
    q_args_dict = expando_to_dict(q_args)
    for k, v in q_args_dict.items():
        DEFAULT_LOGGER.debug(f'{k}: {v}')
    DEFAULT_LOGGER.debug('<<<< q.args <<<<')
