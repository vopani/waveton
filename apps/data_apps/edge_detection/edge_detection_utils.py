import cv2
import numpy as np

from constants import EdgeDetectionKernels


def gaussian_blurring(image: np.array, filter_size: tuple = (5, 5), std: float = 0):
    """
    Apply gaussian blurring for given image.
    """
    return cv2.GaussianBlur(image, filter_size, std)


def edge_detection(
        image: np.array,
        kernel: str = EdgeDetectionKernels.LAPLACE.value,
        edge_detection_kernel_size: int = 3,
        smoothing: bool = False,
        smoothing_kernel_size: int = 3
):
    """
    Apply edge detection for given image.
    """
    if smoothing:
        image = gaussian_blurring(image, (smoothing_kernel_size, smoothing_kernel_size), 0)
    if kernel == EdgeDetectionKernels.LAPLACE.value:
        lap_gradient = cv2.Laplacian(image, cv2.CV_64F, ksize=edge_detection_kernel_size)
        lap_gradient = np.uint(np.absolute(lap_gradient))

        return lap_gradient
    elif kernel == EdgeDetectionKernels.SOBEL.value:
        sob_gradient_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=edge_detection_kernel_size)
        sob_gradient_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=edge_detection_kernel_size)

        sob_gradient_x = np.uint(np.absolute(sob_gradient_x))
        sob_gradient_y = np.uint(np.absolute(sob_gradient_y))

        return cv2.bitwise_or(sob_gradient_x, sob_gradient_y)
