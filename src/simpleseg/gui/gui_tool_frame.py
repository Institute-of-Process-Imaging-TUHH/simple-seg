import tkinter as tk
from tkinter.font import Font
from typing import TYPE_CHECKING

from simpleseg.gui.gui_mpl_tools import AvailableTools
from simpleseg.gui.overlay import AvailableViewModes
from simpleseg.shared_variables import COLORS, N_CLASSES_MAX

if TYPE_CHECKING:
    from simpleseg.app import SegmentationApp
    from simpleseg.gui.gui_mpl_tools import MplTools


RADIO_WIDTH = 20
RADIO_HEIGHT = 3


class ToolFrame(tk.LabelFrame):
    def __init__(self, master, app: "SegmentationApp", mpl_tools: "MplTools", *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)
        self.app = app

        self.app.state._tool_selected_int = tk.IntVar(value=1)
        self.app.state._view_mode_selected_int = tk.IntVar(value=1)
        self.app.state._pencil_width = tk.IntVar(value=5)
        self.app.state._fill_value_pos_int = tk.IntVar(value=1)
        self.app.state._n_classes = tk.IntVar(value=self.app.state._n_classes_init_val)

        # ─── Drawing Tools ────────────────────────────────────────────

        self.drawing_tools_frame = tk.LabelFrame(master=self, text="Tools")

        self.radio_lasso = tk.Radiobutton(
            master=self.drawing_tools_frame,
            text="Lasso",
            indicatoron=0,
            variable=self.app.state._tool_selected_int,
            value=AvailableTools.LASSO.value,
            width=RADIO_WIDTH,
            height=RADIO_HEIGHT,
            command=mpl_tools.activate_tool,
        )
        self.radio_pencil = tk.Radiobutton(
            master=self.drawing_tools_frame,
            text="Pencil",
            indicatoron=0,
            variable=self.app.state._tool_selected_int,
            value=AvailableTools.PENCIL.value,
            width=RADIO_WIDTH,
            height=RADIO_HEIGHT,
            command=mpl_tools.activate_tool,
        )
        self.spinbox_pencil = tk.Spinbox(
            master=self.drawing_tools_frame,
            justify=tk.RIGHT,
            from_=1,
            to=50,
            textvariable=self.app.state._pencil_width,
            width=int(RADIO_WIDTH / 2),
            font=Font(family="Helvetica", size=16, weight="bold"),
        )
        self.label_pencil = tk.Label(master=self.drawing_tools_frame, text="Pencil Width")

        # packing
        self.radio_lasso.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)
        self.radio_pencil.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)
        self.spinbox_pencil.pack(side=tk.RIGHT, anchor="w")
        self.label_pencil.pack(side=tk.RIGHT, anchor="e")
        self.drawing_tools_frame.pack(side=tk.TOP, fill=tk.BOTH)

        # ─── View Actions ─────────────────────────────────────────────

        self.view_frame = tk.LabelFrame(master=self, text="View Options")

        self.radio_viewmode1 = tk.Radiobutton(
            master=self.view_frame,
            text="Overlay",
            indicatoron=0,
            variable=self.app.state._view_mode_selected_int,
            value=AvailableViewModes.OVERLAY.value,
            width=RADIO_WIDTH,
            height=RADIO_HEIGHT,
            command=app.refresh_images,
        )

        self.radio_viewmode2 = tk.Radiobutton(
            master=self.view_frame,
            text="Image only",
            indicatoron=0,
            variable=self.app.state._view_mode_selected_int,
            value=AvailableViewModes.IMG_ONLY.value,
            width=RADIO_WIDTH,
            height=RADIO_HEIGHT,
            command=app.refresh_images,
        )

        self.radio_viewmode3 = tk.Radiobutton(
            master=self.view_frame,
            text="Mask only",
            indicatoron=0,
            variable=self.app.state._view_mode_selected_int,
            value=AvailableViewModes.MASK_ONLY.value,
            width=RADIO_WIDTH,
            height=RADIO_HEIGHT,
            command=app.refresh_images,
        )

        self.view_frame.pack(side=tk.TOP, fill=tk.BOTH)

        # ─── Mask Actions ─────────────────────────────────────────────

        self.radio_viewmode1.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)
        self.radio_viewmode2.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)
        self.radio_viewmode3.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)

        self.file_frame = tk.LabelFrame(master=self, text="Mask Actions")

        self.button_save = tk.Button(
            master=self.file_frame,
            height=RADIO_HEIGHT,
            text="save",
            state=tk.DISABLED,
            command=self.app.save_current_mask,
        )
        self.button_save_all = tk.Button(
            master=self.file_frame,
            height=RADIO_HEIGHT,
            text="save all",
            state=tk.DISABLED,
            command=self.app.save_all_masks,
        )
        self.button_discard = tk.Button(
            master=self.file_frame,
            height=RADIO_HEIGHT,
            text="discard",
            state=tk.DISABLED,
            command=self.app.discard_current_mask,
        )

        # packing
        self.button_save.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)
        self.button_save_all.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)
        self.button_discard.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)
        self.file_frame.pack(side=tk.TOP, fill=tk.BOTH)

        self.classes_frame = tk.LabelFrame(master=self, text="Class Actions")
        self.n_classes_selector_frame = tk.Frame(self.classes_frame)
        self.spinbox_classes = tk.Spinbox(
            master=self.n_classes_selector_frame,
            justify=tk.RIGHT,
            from_=1,
            to=N_CLASSES_MAX,
            textvariable=self.app.state._n_classes,
            width=int(RADIO_WIDTH / 2),
            font=Font(family="Helvetica", size=16, weight="bold"),
            command=self.update_classes_buttons,
        )
        self.label_n_classes = tk.Label(master=self.n_classes_selector_frame, text="n_classes")
        self.n_classes_radio_frame = tk.Frame(master=self.classes_frame)

        # packing
        self.spinbox_classes.pack(side=tk.RIGHT, anchor="w")
        self.label_n_classes.pack(side=tk.RIGHT, anchor="e")
        self.n_classes_selector_frame.pack(side=tk.TOP)
        self.n_classes_radio_frame.pack(side=tk.TOP, fill=tk.X)
        self.classes_frame.pack(side=tk.TOP, fill=tk.BOTH)

        self.update_classes_buttons()

    def update_classes_buttons(self):
        def rgb_to_hex(r: int, g: int, b: int) -> str:
            """r, g, b within 0-255"""
            for v in [r, g, b]:
                assert 0 <= v <= 255
                assert isinstance(v, int)
            return "#{:02x}{:02x}{:02x}".format(r, g, b)

        assert isinstance(self.app.state._fill_value_pos_int, tk.IntVar)

        for widget in self.n_classes_radio_frame.winfo_children():
            widget.destroy()

        for i in range(1, self.app.state.n_classes + 1):
            color_float = COLORS[i - 1]
            color_int_dark = [int(v * 255 * 0.85) for v in color_float]
            color_int_bright = [int(v * 255) for v in color_float]
            hexcolor_dark = rgb_to_hex(*color_int_dark)
            hexcolor_bright = rgb_to_hex(*color_int_bright)
            radio = tk.Radiobutton(
                master=self.n_classes_radio_frame,
                text=f"Class {i}",
                indicatoron=0,
                variable=self.app.state._fill_value_pos_int,
                value=i,
                width=RADIO_WIDTH,
                height=RADIO_HEIGHT,
                selectcolor=hexcolor_bright,
                bg=hexcolor_dark,
            )
            radio.pack(side=tk.TOP, anchor="center", fill=tk.BOTH)

    def update_button_states(self, any_modified: bool, current_modified: bool):
        self.button_save.config(state=tk.NORMAL if current_modified else tk.DISABLED)
        self.button_save_all.config(state=tk.NORMAL if any_modified else tk.DISABLED)
        self.button_discard.config(state=tk.NORMAL if current_modified else tk.DISABLED)
