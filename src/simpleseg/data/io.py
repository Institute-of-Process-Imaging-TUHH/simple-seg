from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from PIL import Image

from simpleseg.validation.data_validation import is_2d_img, is_3d_img, is_float_img


def read_image(image_path: str | Path, dtype=float) -> npt.NDArray[Any]:
    """
    returns an np.array containing the image

    shape:
    for monochrome images the array will be of shape
    (WIDTH, HEIGHT)
    for rgb colored images the array will be of shape
    (WIDTH, HEIGHT, 3)

    value range:
    the value range will be from
    0 to 255 in case of 8 bit
    """
    assert dtype in (float, int)
    if dtype == float:
        return np.asarray(Image.open(image_path), dtype=dtype) / 255
    elif dtype == int:
        return np.asarray(Image.open(image_path), dtype=dtype)
    raise NotImplementedError


def img_2d_to_3d(img: npt.NDArray[Any]) -> npt.NDArray[Any]:
    if is_2d_img(img):
        img = img[:, :, np.newaxis].repeat(3, axis=-1)
    assert is_3d_img(img)
    return img


def img_float_to_uint8(img: npt.NDArray[Any]) -> npt.NDArray[Any]:
    assert is_float_img(img)
    return (img * 255).astype(int)
