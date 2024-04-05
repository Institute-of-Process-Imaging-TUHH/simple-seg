from pathlib import Path

import numpy as np

from simpleseg.data.io import read_image
from simpleseg.validation.data_validation import validate_image_specs

img_rgb_path = Path("test/data/test_image_rgb.jpg")
img_rgb = read_image(img_rgb_path)
img_bw_path = Path("test/data/test_image_bw.jpg")
img_bw = read_image(img_bw_path)


def test_io_image_specs():
    assert validate_image_specs(img_rgb)
    assert validate_image_specs(img_bw)


def test_read_image_rgb_ndim():
    assert img_rgb.ndim == 3


def test_read_image_bw_ndim():
    assert img_bw.ndim == 2


def test_read_image_rgb_3c():
    assert img_rgb.shape[-1] == 3


def test_read_image_rgb_value_range():
    assert np.min(img_rgb) >= 0.0
    assert np.max(img_rgb) <= 1.0
