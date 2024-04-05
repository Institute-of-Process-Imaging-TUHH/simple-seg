import tkinter
import tkinter.ttk
from typing import TYPE_CHECKING

from simpleseg.gui.gui_canvasframe import CanvasFrameMpl
from simpleseg.gui.gui_mpl_tools import MplTools
from simpleseg.gui.gui_tool_frame import ToolFrame
from simpleseg.gui.gui_treeview import TreeViewDatasets, TreeViewFiles

if TYPE_CHECKING:
    from simpleseg.app import SegmentationApp


class GUI:
    def __init__(self, app: "SegmentationApp"):
        # gui definition
        self.app = app
        self.root = tkinter.Tk()
        self.root.state("zoomed")
        self.root.wm_title("SimpleSeg")
        self.root.option_add("*font", "helvetica 9")

        self.canvas_frame = CanvasFrameMpl(master=self.root, app=self.app)
        self.mpl_tools = MplTools(app=self.app, canvas_frame=self.canvas_frame)
        self.sidebar_left = ToolFrame(master=self.root, app=self.app, mpl_tools=self.mpl_tools)
        self.sidebar_right = tkinter.Frame(master=self.root)
        self.sidebar_treeview_frames = TreeViewFiles(master=self.sidebar_right, app=self.app)
        self.sidebar_treeview_datasets = TreeViewDatasets(master=self.sidebar_right)

        self.mpl_tools.activate_tool()

        # packing
        self.sidebar_left.pack(side=tkinter.LEFT, fill="y")
        self.sidebar_right.pack(side=tkinter.RIGHT, fill="y")
        self.sidebar_treeview_datasets.pack(side=tkinter.BOTTOM, fill="x")
        self.sidebar_treeview_frames.pack(side=tkinter.TOP, fill="both", expand=1)
        self.canvas_frame.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=1)

        # set functions
        self.sidebar_treeview_frames.select_func = self.app.set_frame_index
        self.sidebar_treeview_datasets.select_func = self.app.load_dataset_by_id
