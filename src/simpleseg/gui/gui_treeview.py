import tkinter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simpleseg.app import SegmentationApp


class TreeViewFiles(tkinter.LabelFrame):
    def __init__(self, master, app: "SegmentationApp", *args, **kwargs) -> None:
        self.app = app
        self.select_func = lambda x: x  # placeholder
        tkinter.LabelFrame.__init__(self, master, *args, **kwargs)
        self.tree = tkinter.ttk.Treeview(self, columns=("modified", "filename"), show="headings")
        self.tree.column("modified", stretch=tkinter.NO, width=50)
        self.tree.heading("modified", text="mod.")
        self.tree.column("filename", stretch=tkinter.NO, width=350)
        self.tree.heading("filename", text="filename")
        self.tree.bind("<<TreeviewSelect>>", self.onselect)

    def init_tree(self, item_paths: list[str]):
        self.clear_view()
        self.tree_identifiers = []
        for frame_index, string in enumerate(item_paths):
            modified = self.app.mask_is_modified(frame_index)
            modified_string = self.get_modified_string(modified)
            identifier = self.tree.insert("", "end", values=(modified_string, string))
            self.tree_identifiers.append(identifier)
        self.selected_item = None
        self.select(0)
        scrollbar = tkinter.ttk.Scrollbar(self, orient=tkinter.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def update_tree(self, is_modified_list: list[bool]):
        for frame_index, identifier in enumerate(self.tree_identifiers):
            is_modified = is_modified_list[frame_index]
            # modified = self.app.mask_is_modified(frame_index)
            modified_string = self.get_modified_string(is_modified)
            filename_string = self.tree.item(identifier, "values")[1]
            self.tree.item(identifier, values=(modified_string, filename_string))

    @staticmethod
    def get_modified_string(modified: bool) -> str:
        return "[*]" if modified else ""

    def clear_view(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def select(self, i: int) -> None:
        self.selected_item = self.tree_identifiers[i]
        self.tree.focus(self.selected_item)
        self.tree.selection_set(self.selected_item)
        self.tree.see(self.selected_item)

    def onselect(self, event) -> None:
        self.selected_item = self.tree.focus()
        img_id = self.tree.index(self.selected_item)
        self.select_func(img_id)


class TreeViewDatasets(tkinter.LabelFrame):
    """
    displays all datasets on the lower right side
    """

    def __init__(self, master, *args, **kwargs) -> None:
        self.select_func = lambda x: x  # placeholder
        tkinter.LabelFrame.__init__(self, master, text="", *args, **kwargs)
        self.tree = tkinter.ttk.Treeview(self, columns=("datasetname"), show="headings")
        self.tree.column("datasetname", stretch=tkinter.NO, width=400)
        self.tree.heading("datasetname", text="dataset name")
        self.tree.bind("<<TreeviewSelect>>", self.onselect)

    def init_tree(self, dataset_names: list[str]) -> None:
        self.clear_view()
        self.all_tree_inserts = []
        for name in dataset_names:
            insert = self.tree.insert("", tkinter.END, values=(name))
            self.all_tree_inserts.append(insert)
        self.selected_item = None
        self.select(0)
        scrollbar = tkinter.ttk.Scrollbar(self, orient=tkinter.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky=tkinter.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def clear_view(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def select(self, i) -> None:
        self.selected_item = self.all_tree_inserts[i]
        self.tree.focus(self.selected_item)
        self.tree.selection_set(self.selected_item)
        self.tree.see(self.selected_item)

    def onselect(self, event) -> None:
        self.selected_item = self.tree.focus()
        img_id = self.tree.index(self.selected_item)
        self.select_func(img_id)
