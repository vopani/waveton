import os
from enum import Enum

import cv2
from typing import List

from edge_detection_utils import edge_detection


def apply_edge_detection(
        image_paths: List[str],
        processed_folder: str,
        edge_detection_kernel: Enum,
        edge_detection_kernel_size: int,
        smoothing: bool,
        smoothing_kernel_size: int
) -> List[str]:
    """
    Apply edge detection to given list of images.
    """

    processed_images = []

    for image in image_paths:
        img = cv2.imread(image)
        img = edge_detection(
            img, kernel=edge_detection_kernel, edge_detection_kernel_size=edge_detection_kernel_size, smoothing=smoothing, smoothing_kernel_size=smoothing_kernel_size
        )
        cv2.imwrite(os.path.join(processed_folder, f"{os.path.basename(image)}"), img)
        processed_images.append(os.path.join(processed_folder, f"{os.path.basename(image)}"))

    return processed_images
