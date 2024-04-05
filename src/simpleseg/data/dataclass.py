from abc import ABC, abstractmethod
from typing import Any

import numpy.typing as npt


class AbstractData(ABC):
    @abstractmethod
    def __len__(self) -> int:
        """
        Returns the number of samples inside the dataset. Must be 1 or larger.
        """
        ...

    @abstractmethod
    def get_frame_names(self) -> list[str]:
        ...

    @abstractmethod
    def get_image(self, index: int) -> npt.NDArray[Any]:
        """
        returns the image of the specified index as an np.ndarray
        * dtype must be float with values between 0 and 1
        * shape must be one of the following:
            * shape = (WIDTH, HEIGHT)
              -> for monochrome images the array will be of shape
            * shape = (WIDTH, HEIGHT, 3)
              -> for rgb colored images the array will be of shape
        """
        ...

    @abstractmethod
    def get_mask(self, index: int) -> npt.NDArray[Any]:
        """
        returns the mask of the specified index as an np.ndarray
        * dtype must be int with values between 0 and 255
        * shape must be shape = (WIDTH, HEIGHT)
        """
        ...

    @abstractmethod
    def save_mask(self, mask: npt.NDArray[Any], index: int):
        """
        this function handles mask manipulation.
        """
        ...
