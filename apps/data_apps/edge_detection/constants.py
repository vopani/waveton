import logging
from enum import Enum

logging.root.setLevel(logging.DEBUG)

DEFAULT_LOGGER = logging.getLogger("edge-detector-logger")
logging_stream_handler = logging.StreamHandler()
logging_stream_handler.setLevel(logging.DEBUG)
logging_stream_handler.setFormatter(
    logging.Formatter(
        'EDGE-DETECTOR: [%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        '%m-%d %H:%M:%S'
    )
)
DEFAULT_LOGGER.addHandler(logging_stream_handler)


class EdgeDetectionKernels(Enum):
    LAPLACE = 'LAPLACE'
    SOBEL = 'SOBEL'


DROPPABLE_CARDS = [
    'error',
    'commands_panel',
    'original_image_viewer',
    'processed_image_viewer',
    'image_table'
]
