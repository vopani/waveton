import os
from enum import Enum

import cv2
import pandas as pd

from datetime import datetime
from typing import Union, List

from edge_detection_utils import edge_detection


def update_image_df(image_df: pd.DataFrame, image_paths: Union[str, List]):
    temp = pd.DataFrame({
        'Image': [image_paths] if type(image_paths) == str else image_paths,
        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    return image_df.append(temp, ignore_index=True)


def apply_edge_detection(
        image_paths: List[str],
        processed_folder: str,
        edge_detection_kernel: Enum,
        smoothing: bool,
        smoothing_kernel_size: int
) -> List[str]:

    processed_images = []

    for image in image_paths:
        img = cv2.imread(image)
        img = edge_detection(
            img, kernel=edge_detection_kernel, smoothing=smoothing, smoothing_kernel_size=smoothing_kernel_size
        )
        cv2.imwrite(os.path.join(processed_folder, f"{os.path.basename(image)}"), img)
        processed_images.append(os.path.join(processed_folder, f"{os.path.basename(image)}"))

    return processed_images
