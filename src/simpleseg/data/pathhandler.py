# %%
import csv
import time
from pathlib import Path
from typing import Optional

from loguru import logger
from simpleseg.data.io import read_image


class PathHandler:
    def __init__(self, root_dirs: str | Path | list[str | Path]):
        if isinstance(root_dirs, str):
            root_dirs_out = [Path(root_dirs)]
        elif isinstance(root_dirs, Path):
            root_dirs_out = [root_dirs]
        elif isinstance(root_dirs, list):
            root_dirs_out = [Path(item) for item in root_dirs]
        assert all([isinstance(item, Path) for item in root_dirs_out])
        self.root_dirs: list[Path] = root_dirs_out

        self.item_paths = []
        self.counter_imgs = 0
        self.counter_masks = 0

        for root_dir in self.root_dirs:
            assert root_dir.is_dir()
            item_paths_dir = self.search_through_dir(root_dir=root_dir)
            self.item_paths.extend(item_paths_dir)

    def write_row(self, csv_file, row: list):
        with csv_file.open(mode="a", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(row)

    @staticmethod
    def find_path_from_index(paths: list[Path], search_str: str) -> Optional[Path]:
        for path in paths:
            if search_str in str(path):
                return path
        return None

    def search_through_dir(self, root_dir: Path):
        assert isinstance(root_dir, Path)
        item_paths_dir = []
        t0 = time.perf_counter()

        # imgs
        imgs_dir = root_dir / "imgs"
        imgs_paths = list(imgs_dir.glob("*"))

        # imgs norm
        imgs_norm_dir = root_dir / "imgs_normalized"
        imgs_norm_paths = list(imgs_norm_dir.glob("*"))

        # masks
        masks_dir = root_dir / "masks"
        masks_paths = list(masks_dir.glob("*"))

        # weight binary
        weight_binary_file = next(root_dir.glob("weights_binary*"), None)
        weight_gradient_file = next(root_dir.parent.glob("weights_gradient*"), None)

        for index in range(10000000):
            number_string = str(index).zfill(5)

            img_path = self.find_path_from_index(imgs_paths, number_string)
            imgs_norm_path = self.find_path_from_index(imgs_norm_paths, number_string)
            mask_path = self.find_path_from_index(masks_paths, number_string)

            if img_path is None:
                break

            logger.info("loading image with index ", index)

            self.counter_imgs += 1
            if mask_path:
                self.counter_masks += 1

            item_paths_dir.append(
                {
                    "image": img_path,
                    "image_norm": imgs_norm_path,
                    "mask": mask_path,
                    "weight_binary": weight_binary_file,
                    "weight_gradient": weight_gradient_file,
                }
            )

        logger.info(f"found {self.counter_imgs} imgs, {self.counter_masks} masks in {time.perf_counter() - t0} seconds")
        return item_paths_dir

    def __getitem__(self, idx) -> dict[str, Optional[Path]]:
        return self.item_paths[idx]

    def __len__(self):
        return len(self.item_paths)

    def __repr__(self):
        dir_string = "loaded directories: \n"
        for path in self.root_dirs:
            dir_string += str(path) + "\n"
        return f"filehandler with {self.counter_imgs} images and {self.counter_masks} masks \n" + dir_string

    def get_image(self, idx: int):
        img_path = self.item_paths[idx]["img_path"]
        return read_image(img_path)

    def get_mask(self, idx: int):
        mask_path = self.item_paths[idx]["mask_path"]
        return read_image(mask_path)
