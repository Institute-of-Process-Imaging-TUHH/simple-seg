import time
from abc import ABC, abstractmethod
from enum import IntEnum, auto
from itertools import chain
from typing import TYPE_CHECKING, Any, Optional

import numpy as np
import numpy.typing as npt
from loguru import logger
from matplotlib.backend_bases import Event, MouseButton, MouseEvent
from matplotlib.patches import Ellipse, Patch
from matplotlib.path import Path as mplPath
from matplotlib.widgets import LassoSelector
from simpleseg.gui.gui_canvasframe import CanvasFrameMpl
from simpleseg.validation.data_validation import is_2d_img, is_int_img
from skimage.segmentation import flood_fill

if TYPE_CHECKING:
    from simpleseg.app import AppState, SegmentationApp


class AvailableTools(IntEnum):
    LASSO = auto()
    PENCIL = auto()


class MplTools:
    def __init__(self, app: "SegmentationApp", canvas_frame: CanvasFrameMpl):
        self.app: SegmentationApp = app
        self.state: AppState = self.app.state
        self.canvas_frame: CanvasFrameMpl = canvas_frame

        self.tool: Optional[Tool] = None
        self.tools = {AvailableTools.LASSO: ToolLasso(mplTools=self), AvailableTools.PENCIL: ToolPencil(mplTools=self)}

        # self.activate_tool()

    def activate_tool(self):
        assert self.app.state.tool_selected in AvailableTools
        if self.tool is not None:
            self.tool.deactivate()
        self.tool = self.tools[self.app.state.tool_selected]
        self.tool.activate()

    @property
    def fill_value(self) -> int:
        if self.state.active_mouse_button is MouseButton.LEFT:
            return self.state.fill_value_pos
        elif self.state.active_mouse_button is MouseButton.RIGHT:
            return self.state.fill_value_neg
        else:
            logger.warning("unknown state.active_mouse_button, cannot apply lasso_on_select")
            return 1


class Tool(ABC):
    def __init__(self, mplTools: MplTools):
        self.mplTools = mplTools
        self.app = self.mplTools.app
        self.state = self.app.state
        self.canvas_frame = self.mplTools.canvas_frame
        self.canvas = self.canvas_frame.canvas
        self.ax = self.canvas_frame.ax

    @abstractmethod
    def activate(self):
        ...

    @abstractmethod
    def deactivate(self):
        ...


ERASER = False


class ToolPencil(Tool):
    def __init__(self, mplTools: MplTools):
        super().__init__(mplTools=mplTools)
        self.visual_patch: Optional[Patch] = None

        self.lastx: Optional[int] = None
        self.lasty: Optional[int] = None

    def activate(self):
        self.cids = []
        self.cids.append(self.canvas.mpl_connect("button_press_event", self.init_draw_coords))
        self.cids.append(self.canvas.mpl_connect("motion_notify_event", self.draw_coords))
        self.cids.append(self.canvas.mpl_connect("button_release_event", self.stop_drawing))

    def deactivate(self):
        for cid in self.cids:
            self.canvas.mpl_disconnect(cid)
        self.cids = []

    def update_drawing_mask(self):
        width = self.state.pencil_width
        self.drawing_mask = bresenham_circle_mask(width)

    def init_draw_coords(self, event: MouseEvent):
        self.img_3d = self.app.img_2d_to_3d(self.app.get_current_img())
        self.mask_temp = self.app.get_current_mask().copy()
        self.update_drawing_mask()
        self.draw_coords(event)

    def draw_coords(self, event: MouseEvent) -> None:
        if not isinstance(event, MouseEvent):
            return

        self.remove_contour()
        if event.inaxes != self.ax:
            return

        if event.button == 1 or event.button == 3:
            self.mask_temp = self.update_matrix(event, self.mask_temp)
            overlay = self.app.get_overlay(self.img_3d, self.mask_temp)
            self.canvas_frame.im.set_data(overlay)

        self.ax.draw_artist(self.canvas_frame.im)

        artist = self.get_artist(event)
        self.ax.add_patch(artist)
        self.ax.draw_artist(artist)

        self.canvas.blit(self.ax.bbox)

    def update_matrix(self, event: MouseEvent, in_matrix: npt.NDArray[Any]) -> npt.NDArray[Any]:
        newx = int(np.round(event.xdata))
        newy = int(np.round(event.ydata))

        if newx == self.lastx and newy == self.lasty:
            return in_matrix

        xcoords, ycoords = bresenham_line(self.lastx, self.lasty, newx, newy)
        xs = self.drawing_mask[0] + xcoords[None].T
        ys = self.drawing_mask[1] + ycoords[None].T

        # clipping to set range
        xcoords = xs.flatten().clip(0, self.app.resolution[1])
        ycoords = ys.flatten().clip(0, self.app.resolution[0])

        idcs = (ycoords, xcoords)
        in_matrix[idcs] = self.mplTools.fill_value

        self.lastx = newx
        self.lasty = newy

        return in_matrix

    def stop_drawing(self, event: Event) -> None:
        self.lastx = None
        self.lasty = None
        assert is_2d_img(self.mask_temp)
        self.app.set_current_mask(self.mask_temp)

    def get_artist(self, event: MouseEvent) -> Ellipse:
        outlineprops = {"linewidth": 5, "alpha": 0.8, "facecolor": "none"}
        outlineprops["edgecolor"] = "red" if ERASER else "lime"
        width = self.state.pencil_width
        x, y = event.xdata, event.ydata
        offset = -0.5 if width % 2 == 0 else 0
        self.visual_patch = Ellipse((x + offset, y + offset), width, width, **outlineprops)
        return self.visual_patch

    def remove_contour(self) -> None:
        if self.visual_patch is not None:
            self.visual_patch.remove()
            self.visual_patch = None


class ToolLasso(Tool):
    def __init__(self, mplTools: MplTools):
        super().__init__(mplTools=mplTools)
        self.lasso = LassoSelector(self.ax, onselect=self.lasso_on_select)
        self.lasso.disconnect_events()

    def activate(self):
        self.lasso.connect_default_events()

    def deactivate(self):
        self.lasso.disconnect_events()

    def lasso_on_select(self, verts):
        logger.debug("time: lasso_on_select")
        t0 = time.perf_counter()
        path = mplPath(verts)
        xv, yv = np.meshgrid(np.arange(self.app.resolution[0]), np.arange(self.app.resolution[1]))
        point_coords = np.vstack((yv.flatten(), xv.flatten())).T  # all pixels (x,y) as N x 2 array
        contains_points = path.contains_points(point_coords).reshape(self.app.resolution[:2], order="F")
        mask = self.app.get_current_mask()
        assert is_2d_img(mask)
        assert is_int_img(mask)
        assert isinstance(self.mplTools.fill_value, int)
        mask[contains_points] = self.mplTools.fill_value
        logger.debug(time.perf_counter() - t0)
        self.app.set_current_mask(mask)


def bresenham_circle_mask(width: int):
    """Efficient way of creating a circular drawing mask"""

    assert isinstance(width, int)
    assert width >= 1, "width must be 1 or larger"

    radius = width // 2
    if width % 2 == 0:
        radius -= 1

    coords_set = set()
    f = 1 - radius
    ddF_x = 0
    ddF_y = -2 * radius
    x = 0
    y = radius

    offset = 0
    if width % 2 == 0:
        offset = -1
        coords_set.add((offset, radius))
        coords_set.add((radius, offset))
        coords_set.add((offset, -radius + offset))
        coords_set.add((-radius + offset, offset))
    coords_set.add((0, radius))
    coords_set.add((radius, 0))
    coords_set.add((0, -radius + offset))
    coords_set.add((-radius + offset, 0))

    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x + 1

        coords_set.add((x, y))
        coords_set.add((-x + offset, y))
        coords_set.add((x, -y + offset))
        coords_set.add((-x + offset, -y + offset))
        coords_set.add((y, x))
        coords_set.add((-y + offset, x))
        coords_set.add((y, -x + offset))
        coords_set.add((-y + offset, -x + offset))

    arr = np.fromiter(chain.from_iterable(coords_set), int)
    num_coords = len(coords_set)
    arr.shape = num_coords, 2

    # filling cirlce with 1 to generate mask depending on pencil width
    min_val = arr.min()
    val_range = arr.max() - min_val
    temp_mask = np.zeros((val_range + 1, val_range + 1))
    temp_mask[arr[:, 0] - min_val, arr[:, 1] - min_val] = 1
    flood_mask = flood_fill(temp_mask, (abs(min_val), abs(min_val)), 1, connectivity=1)
    idcs = np.where(flood_mask == 1)
    return idcs[0] + min_val, idcs[1] + min_val  # xcoords, ycoords


def bresenham_line(x0, y0, x1, y1) -> tuple[npt.NDArray[Any], npt.NDArray[Any]]:
    """Returns coordinates of a line connecting two points."""

    if x0 is None or y0 is None:
        return np.array([x1]), np.array([y1])

    xcoords = []
    ycoords = []
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy  # error value e_xy

    while True:
        xcoords.append(x0)
        ycoords.append(y0)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > dy:
            err += dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return np.array(xcoords, dtype=int), np.array(ycoords, dtype=int)
