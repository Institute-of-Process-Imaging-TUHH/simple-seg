from typing import Any

import numpy as np
import numpy.typing as npt


def validate_mask_specs(img: npt.NDArray[Any]) -> bool:
    return all([is_2d_img(img), is_int_img(img)])


def validate_image_specs(img: npt.NDArray[Any]) -> bool:
    return all([is_2d_img(img) or is_3d_img(img), is_float_img(img)])


def is_3d_img(img: npt.NDArray[Any]) -> bool:
    """
    checks for:
    * ndim == 3
    * shape[-1] == 3
    """
    return all([isinstance(img, np.ndarray), img.ndim == 3, img.shape[-1] == 3])


def is_2d_img(img: npt.NDArray[Any]) -> bool:
    """
    checks for:
    * ndim == 2
    """
    return all([isinstance(img, np.ndarray), img.ndim == 2])


def is_float_img(img: npt.NDArray[Any]) -> bool:
    """
    checks for:
    * dtype == float
    * min value >= 0.0
    * max value <= 1.0
    """
    return all([isinstance(img, np.ndarray), img.dtype == float, img.min() >= 0.0, img.max() <= 1.0])


def is_int_img(img: npt.NDArray[Any]) -> bool:
    """
    checks for:
    * dtype == int
    * min value >= 0
    * max value <= 255
    """
    return all([isinstance(img, np.ndarray), img.dtype == int, img.min() >= 0, img.max() <= 255])
