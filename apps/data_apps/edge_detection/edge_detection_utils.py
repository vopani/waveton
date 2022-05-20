import cv2
import numpy as np

from constants import EdgeDetectionKernels


def gaussian_blurring(image: np.array, filter_size: tuple = (5, 5), std: float = 0):
    return cv2.GaussianBlur(image, filter_size, std)


def edge_detection(image: np.array, kernel: str = EdgeDetectionKernels.LAPLACE, smoothing: bool = False):
    if smoothing:
        image = gaussian_blurring(image, (3, 3), 0)
    if kernel == EdgeDetectionKernels.LAPLACE:
        lap_gradient = cv2.Laplacian(image, cv2.CV_64F)
        lap_gradient = np.uint(np.absolute(lap_gradient))

        return lap_gradient
    elif kernel == EdgeDetectionKernels.SOBEL:
        sob_gradient_x = cv2.Sobel(image, cv2.CV_64F, 1, 0)
        sob_gradient_y = cv2.Sobel(image, cv2.CV_64F, 0, 1)

        sob_gradient_x = np.uint(np.absolute(sob_gradient_x))
        sob_gradient_y = np.uint(np.absolute(sob_gradient_y))

        return cv2.bitwise_or(sob_gradient_x, sob_gradient_y)
