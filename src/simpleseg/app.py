import time
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import numpy.typing as npt
from loguru import logger
from matplotlib.backend_bases import MouseButton

from simpleseg.data.dataclass import AbstractData
from simpleseg.gui.gui import GUI
from simpleseg.gui.gui_canvasframe import CanvasFrameMpl
from simpleseg.gui.gui_mpl_tools import AvailableTools
from simpleseg.gui.gui_tool_frame import ToolFrame
from simpleseg.gui.gui_treeview import TreeViewDatasets, TreeViewFiles
from simpleseg.gui.overlay import AvailableViewModes, ViewModeSelector
from simpleseg.shared_variables import N_CLASSES_MAX
from simpleseg.validation.data_validation import is_2d_img, is_3d_img, is_float_img, is_int_img


@dataclass
class AppState:
    _n_classes_init_val: int
    fill_value_neg: int = 0
    active_mouse_button: MouseButton = None
    _n_classes: Optional[tk.IntVar] = None
    _fill_value_pos_int: Optional[tk.IntVar] = None
    _pencil_width: Optional[tk.IntVar] = None
    _tool_selected_int: Optional[tk.IntVar] = None
    _view_mode_selected_int: Optional[tk.IntVar] = None

    @property
    def n_classes(self) -> int:
        if self._n_classes:
            val = self._n_classes.get()
            if 1 <= val <= N_CLASSES_MAX:
                return val
        logger.warning("n_classes could not be derived from tk.IntVar")
        return 1

    @property
    def fill_value_pos(self) -> int:
        if self._fill_value_pos_int:
            val = self._fill_value_pos_int.get()
            assert 1 <= val <= N_CLASSES_MAX
            return val
        logger.warning("fill_value_pos could not be derived from tk.IntVar")
        return 1

    @property
    def pencil_width(self) -> int:
        if self._pencil_width:
            pencil_width = self._pencil_width.get()
            if 1 <= pencil_width <= 100:
                return pencil_width
        logger.warning("pencil width could not be derived from tk.IntVar")
        return 5

    @property
    def tool_selected(self) -> AvailableTools:
        assert isinstance(self._tool_selected_int, tk.IntVar)
        return AvailableTools(self._tool_selected_int.get())

    @property
    def view_strategy_selected(self):
        assert isinstance(self._view_mode_selected_int, tk.IntVar)
        return AvailableViewModes(self._view_mode_selected_int.get())


class SegmentationApp:
    cache_img: dict[int, npt.NDArray[Any]] = dict()
    cache_mask: dict[int, npt.NDArray[Any]] = dict()
    cache_mask_overwrite: dict[int, npt.NDArray[Any]] = dict()

    def __init__(
        self,
        datasets: list[AbstractData],
        n_classes: int = 1,
    ) -> None:
        assert isinstance(n_classes, int)
        assert 1 <= n_classes <= N_CLASSES_MAX
        self.state = AppState(_n_classes_init_val=n_classes)

        self.gui = GUI(app=self)
        self.tool_frame: ToolFrame = self.gui.sidebar_left
        self.view_mode_selector = ViewModeSelector(self.state)
        self.canvas_frame: CanvasFrameMpl = self.gui.canvas_frame
        self.tree_frames: TreeViewFiles = self.gui.sidebar_treeview_frames
        self.tree_datasets: TreeViewDatasets = self.gui.sidebar_treeview_datasets

        self.datasets: list[AbstractData] = datasets
        self.dataset_names: list[str] = [item.name for item in datasets]
        self.tree_datasets.init_tree(self.dataset_names)

        self.load_dataset_by_id(0)
        tk.mainloop()

    def reset_caches(self) -> None:
        self.cache_img.clear()
        self.cache_mask.clear()
        self.cache_mask_overwrite.clear()

    def get_img(self, index) -> npt.NDArray[Any]:
        if index in self.cache_img:
            return self.cache_img[index]
        else:
            img = self.dataset.get_image(index)
            assert is_float_img(img)
            assert img.shape == self.resolution
            self.cache_img[index] = img
            return img

    def get_mask(self, index) -> npt.NDArray[Any]:
        if index in self.cache_mask_overwrite:
            return self.cache_mask_overwrite[index]
        elif index in self.cache_mask:
            return self.cache_mask[index].copy()
        else:
            mask = self.dataset.get_mask(index)
            assert is_int_img(mask)
            assert mask.shape == self.resolution[:2]
            self.cache_mask[index] = mask
            return mask

    def save_mask(self, frame_index: int):
        if frame_index not in self.cache_mask_overwrite:
            logger.warn("cannot save_mask(), index not in cache_mask_overwrite")
            return
        old_mask = self.dataset.get_mask(frame_index)
        new_mask = self.cache_mask_overwrite[frame_index]
        if old_mask.shape != new_mask.shape:
            logger.error("cannot save_mask(), shape of new and old mask mismatch")
            return
        assert is_int_img(new_mask)
        assert is_2d_img(new_mask)
        self.dataset.save_mask(new_mask, frame_index)
        self.cache_mask[frame_index] = self.cache_mask_overwrite[frame_index]
        self.discard_mask(frame_index)

    def save_current_mask(self):
        self.save_mask(self.current_frame_index)

    def save_all_masks(self):
        for frame_index in self.cache_mask_overwrite.keys():
            self.save_mask(frame_index)

    def discard_mask(self, frame_index: int):
        del self.cache_mask_overwrite[frame_index]
        self.refresh_images()
        self.refresh_modified_masks_state()
        self.update_button_states()
        self.update_tree_list()

    def discard_current_mask(self):
        self.discard_mask(self.current_frame_index)

    def get_current_img(self) -> npt.NDArray[Any]:
        frame_index = self.current_frame_index
        return self.get_img(frame_index)

    def get_current_mask(self) -> npt.NDArray[Any]:
        frame_index = self.current_frame_index
        return self.get_mask(frame_index)

    def set_current_mask(self, mask: npt.NDArray[Any], update: bool = True):
        assert is_2d_img(mask)
        assert is_int_img(mask)
        frame_index = self.current_frame_index
        self.cache_mask_overwrite[frame_index] = mask
        if update:
            self.update_all_new_func()

    def update_all_new_func(self):
        self.refresh_images()
        self.refresh_modified_masks_state()
        self.update_button_states()
        self.update_tree_list()

    def update_button_states(self):
        current_modified = self.is_modified_list[self.current_frame_index]
        self.tool_frame.update_button_states(any_modified=self.any_frame_modified, current_modified=current_modified)

    def update_tree_list(self):
        self.tree_frames.update_tree(self.is_modified_list)

    def refresh_modified_masks_state(self):
        self.is_modified_list = [self.mask_is_modified(index) for index in range(self.n)]
        self.any_frame_modified = any(self.is_modified_list)

    def set_frame_index_prev(self):
        self.set_frame_index(self.current_frame_index - 1)

    def set_frame_index_next(self):
        self.set_frame_index(self.current_frame_index + 1)

    def set_frame_index(self, frame_index: int):
        self.current_frame_index = frame_index
        self.check_frame_range()
        self.refresh_images()
        self.update_button_states()

    def check_frame_range(self):
        lower_boundary = 0
        upper_boundary = self.n
        if self.current_frame_index < lower_boundary:
            self.current_frame_index = upper_boundary
        if self.current_frame_index > upper_boundary:
            self.current_frame_index = lower_boundary

    def load_dataset_by_id(self, dataset_id: int):
        dataset = self.datasets[dataset_id]
        self.load_dataset(dataset)

    def mask_is_modified(self, frame_index: int) -> bool:
        return frame_index in self.cache_mask_overwrite.keys()

    def load_dataset(self, dataset: AbstractData):
        self.dataset = dataset
        self.n = len(dataset)
        self.resolution = dataset.get_image(0).shape
        self.canvas_frame.init_imshow(self.resolution)
        self.reset_caches()
        self.refresh_modified_masks_state()
        self.tree_frames.init_tree(dataset.get_frame_names())
        self.set_frame_index(0)
        self.refresh_images()

    def get_mask_dirs_of_dataset(self, dataset_path: Path) -> list[Path]:
        dataset_path = Path(dataset_path)
        mask_dirs = [f for f in dataset_path.iterdir() if f.is_dir() and "masks" in str(f)]
        return mask_dirs

    def img_2d_to_3d(self, img: npt.NDArray[Any]) -> npt.NDArray[Any]:
        if is_2d_img(img):
            img = img[..., None].repeat(3, axis=-1)
        assert is_3d_img(img)
        return img

    def refresh_images(self):
        """
        here all images are float
        """
        logger.debug("time: refresh_images")
        t0 = time.perf_counter()

        special_3d_float = self.get_current_overlay()
        self.canvas_frame.draw_images(special_3d_float)

        logger.debug(time.perf_counter() - t0)

    def get_current_overlay(self):
        img = self.get_current_img()
        mask = self.get_current_mask()
        special_3d_float = self.view_mode_selector.get_view(img, mask)
        return special_3d_float

    def get_overlay(self, img: npt.NDArray[Any], mask: npt.NDArray[Any]) -> npt.NDArray[Any]:
        """
        img: 2d or 3d, float
        mask: 2d, int
        out: 3d, float
        """
        return self.view_mode_selector.get_view(img, mask)
