import pandas as pd

from datetime import datetime
from typing import Union, List


def update_image_df(image_df: pd.DataFrame, image_paths: Union[str, List]):
    temp = pd.DataFrame({
        'Image': [image_paths] if type(image_paths) == str else image_paths,
        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    return image_df.append(temp, ignore_index=True)