from abc import ABC, abstractmethod
from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any

import numpy as np
import numpy.typing as npt
from simpleseg.data.io import img_2d_to_3d
from simpleseg.shared_variables import COLORS
from simpleseg.validation.data_validation import is_2d_img, is_3d_img, is_float_img, is_int_img

if TYPE_CHECKING:
    from simpleseg.app import AppState


class AvailableViewModes(IntEnum):
    OVERLAY = auto()
    IMG_ONLY = auto()
    MASK_ONLY = auto()


class ViewModeSelector:
    def __init__(self, state: "AppState"):
        self.state = state
        self.view_strategies: dict[AvailableViewModes, type[ViewStrategy]] = {
            AvailableViewModes.OVERLAY: OverlayView,
            AvailableViewModes.IMG_ONLY: ImgOnlyView,
            AvailableViewModes.MASK_ONLY: MaskOnlyView,
        }

    def get_view(self, img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        view_strategy: type[ViewStrategy] = self.view_strategies[self.state.view_strategy_selected]
        return view_strategy.get_view(img, mask)


class ViewStrategy(ABC):
    @classmethod
    def get_view(cls, img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        img_3d = img_2d_to_3d(img)
        assert is_float_img(img_3d)
        assert is_3d_img(img_3d)
        assert is_2d_img(mask)
        assert is_int_img(mask)
        return cls._get_view(img_3d, mask)

    @staticmethod
    @abstractmethod
    def _get_view(img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        ...


class ImgOnlyView(ViewStrategy):
    @staticmethod
    def _get_view(img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        return img


class MaskOnlyView(ViewStrategy):
    @staticmethod
    def _get_view(img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        assert is_int_img(mask)
        if np.max(mask) <= 1:
            # only one class
            mask_2d = mask.astype(float)
            mask_3d = img_2d_to_3d(mask_2d)
        else:
            # many classes
            mask_3d = colorize_mask(mask)
        assert is_float_img(mask_3d)
        return mask_3d


class OverlayView(ViewStrategy):
    @staticmethod
    def _get_view(img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        if mask.max() > 1:
            return OverlayMultiView._get_view(img, mask)
        else:
            return OverlaySingleView._get_view(img, mask)


class OverlaySingleView(ViewStrategy):
    @staticmethod
    def _get_view(img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """
        generates a mask visualization for binary masks
        img: 3d float
        mask: 2d int
        """
        # checks
        assert is_3d_img(img)
        assert is_float_img(img)
        assert is_2d_img(mask)
        assert is_int_img(mask)

        # combine matrices
        out = img.copy()
        out[:, :, 2] = np.where(mask[:, :] > 0, 1, 0)

        # check output
        assert is_3d_img(out)
        assert is_float_img(out)
        return out


class OverlayMultiView(ViewStrategy):
    @staticmethod
    def _get_view(img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """
        generates a mask visualization for binary masks
        img: 3d float
        mask: 2d int
        """
        # checks
        assert is_3d_img(img)
        assert is_float_img(img)
        assert is_2d_img(mask)
        assert is_int_img(mask)

        # combine matrices
        mask_colorized = colorize_mask(mask)

        WEIGHT_IMG = 1.0
        WEIGHT_MASK = 1.0
        out = (WEIGHT_IMG * img + WEIGHT_MASK * mask_colorized) / (WEIGHT_IMG + WEIGHT_MASK)

        # check output
        assert is_3d_img(out)
        assert is_float_img(out)
        return out


def colorize_mask(mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
    out = np.zeros((*mask.shape, 3), dtype=float)  # shape: height x width x 3
    classes = np.unique(mask).tolist()  # returns [1, 2, 3] if classes 0, 1, 2, 3 are present in mask
    classes.remove(0)
    for class_int in classes:
        mask_class = (mask == class_int)[..., None]
        color = COLORS[class_int - 1]
        color_array = np.array(color)[None, None, ...]
        out = np.where(mask_class.repeat(3, axis=-1), color_array, out)
    return out
