import logging
import tkinter
import tkinter.ttk
from typing import TYPE_CHECKING

import numpy as np
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseButton, key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.image import AxesImage
from simpleseg.validation.data_validation import is_3d_img, is_float_img

if TYPE_CHECKING:
    from simpleseg.app import SegmentationApp

logger = logging.getLogger(__name__)


class CanvasFrameMpl(tkinter.LabelFrame):
    def __init__(self, master, app: "SegmentationApp") -> None:
        self.app = app
        self.state = self.app.state
        self.width = master.winfo_screenwidth()
        self.height = master.winfo_screenheight()

        self.fig = Figure(figsize=(15, 10), dpi=100)
        self.ax: Axes = self.fig.subplots()  # is used outside, should not be recreated!
        # self.ax.axis(False)
        self.im = None

        # ─── Tkinter ──────────────────────────────────────────────────
        tkinter.LabelFrame.__init__(self, master)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # bindings
        self.canvas.mpl_connect("key_press_event", key_press_handler)

        # mouse stuff
        self.canvas.mpl_connect("button_press_event", self.set_mouse_button)
        self.canvas.mpl_connect("button_press_event", self.print_event)
        self.canvas.mpl_connect("button_release_event", self.print_event)

        # keyboard stuff
        self.canvas.mpl_connect("key_press_event", self.print_event)
        self.canvas.mpl_connect("key_release_event", self.print_event)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()

        self.canvas.get_tk_widget().focus_set()

    def init_imshow(self, shape) -> None:
        matrix = np.zeros(shape=shape, dtype=int)
        self.im = self.ax.imshow(matrix, aspect="equal", vmin=0, vmax=1)

    def draw_images(self, matrix) -> None:
        """
        img:     height x width x 3   -   0 to 1
        mask:    height x width x 3   -   0 to 1
        special: height x width x 3   -   0 to 1
        """

        assert is_3d_img(matrix)
        assert is_float_img(matrix)
        if isinstance(self.im, AxesImage):
            self.im.set_data(matrix)
        self.canvas.draw_idle()

    def restore_focus(self, event=None) -> None:
        logger.info("set focus")
        self.canvas.get_tk_widget().focus_set()

    def set_mouse_button(self, event) -> None:
        mouse_button: MouseButton = event.button
        if isinstance(mouse_button, MouseButton):
            self.state.active_mouse_button = mouse_button
        else:
            logger.warning("unknown button type, could not set state.active_mouse_button")

    def print_event(self, event) -> None:
        pass
