import re
from pathlib import Path
from typing import Any, Optional

import numpy as np
import numpy.typing as npt
from loguru import logger
from PIL import Image
from simpleseg import AbstractData
from simpleseg.data.io import read_image
from simpleseg.validation.data_validation import is_2d_img, is_3d_img, is_float_img, is_int_img


class DemoData(AbstractData):
    def __init__(self, dataset_path: Path, name: str):
        assert isinstance(dataset_path, Path)
        self.dataset_path = dataset_path
        self.name = name.replace(" ", "_")
        self.path_handler = PathHandler(dataset_path)

    def __len__(self) -> int:
        return len(self.path_handler)

    def get_frame_names(self) -> list[str]:
        """
        frame names will be displayed in file list (right side)
        """
        return [path["image"].name for path in self.path_handler.item_paths]

    def get_image(self, index: int) -> npt.NDArray[Any]:
        img_path = self.path_handler[index]["image"]
        assert isinstance(img_path, Path)
        img = read_image(img_path, dtype=float)
        assert is_float_img(img)
        assert is_2d_img(img) or is_3d_img(img)
        return img

    def get_mask(self, index: int) -> npt.NDArray[Any]:
        mask_path: Optional[Path] = self.path_handler[index]["mask"]
        assert isinstance(mask_path, Path)
        if mask_path.is_file():
            mask = read_image(mask_path, dtype=int)
        else:
            logger.info(f"mask with frame_index {index} not found")
            mask = self.get_image(index).copy()
            if is_3d_img(mask):
                mask = mask[..., 0]
            mask.fill(0)
            mask = mask.astype(int)
        assert is_int_img(mask)
        assert is_2d_img(mask)

        # temp stuff
        if np.unique(mask).tolist() == [0, 255]:
            mask = (mask / 255).astype(int)

        return mask

    def save_mask(self, mask: npt.NDArray[Any], index: int) -> None:
        assert is_int_img(mask)
        assert is_2d_img(mask)
        path = self.path_handler[index]["mask"]
        mask = mask.astype(np.uint8)
        im = Image.fromarray(mask)
        assert isinstance(path, Path)
        im.save(path)


class PathHandler:
    def __init__(self, root_dir: Path) -> None:
        assert root_dir.is_dir()
        self.root_dir = root_dir
        self.item_paths: list[dict[str, Path]] = self.scan_dir(self.root_dir)

    def scan_dir(self, root_dir: Path) -> list[dict[str, Path]]:
        """
        finds all samples of the dataset, when the the dir structure is as follows

        dataset/
            imgs/
                somename-frame-0001.jpg
                somename-frame-0002.jpg
                somename-frame-0003.jpg
                somename-frame-0...
            masks/
                someothername-frame-0001.jpg
                someothername-frame-0002.jpg
                someothername-frame-0003.jpg
                someothername-frame-0...

        and returns them in an object of the shape list[dict[str, Path]]:
        [
            {
            "image": image-0001-path,
            "mask": mask-0001-path,
            },
            {
            "image": image-0002-path,
            "mask": mask-0002-path,
            },
            {
            "image": image-0...-path,
            "mask": mask-0...-path,
            },
        ]
        """

        def find_mask(masks_paths: list[Path], search_string: str) -> Optional[Path]:
            for path in masks_paths:
                if search_string in path.name:
                    return path
            return None

        item_paths = []
        imgs_dir = root_dir / "imgs"
        imgs_paths = imgs_dir.glob("*")
        masks_dir = root_dir / "masks"
        masks_paths = list(masks_dir.glob("*"))

        for img_path in imgs_paths:
            match = re.search(r"frame-(\d+)", img_path.name)
            assert match
            number_string = match[1]
            mask_path = find_mask(masks_paths, number_string)
            if mask_path is None:
                mask_path = masks_dir / img_path.name
            assert isinstance(img_path, Path)
            assert isinstance(mask_path, Path)
            item_paths.append(
                {
                    "image": img_path,
                    "mask": mask_path,
                }
            )

        return item_paths

    def __getitem__(self, idx) -> dict[str, Path]:
        return self.item_paths[idx]

    def __len__(self) -> int:
        return len(self.item_paths)
