# -*- coding: utf-8 -*-
"""文件/文件夹列表视图（Treeview 封装）。"""
import tkinter as tk
from tkinter import ttk

__all__ = ["FileList"]

COLUMNS = ("名称", "类型", "大小", "修改时间", "位置")


class FileList:
    """封装 Treeview，向控制器（MainWindow）回传交互事件。"""

    def __init__(self, parent, controller):
        self.controller = controller
        self.tree = ttk.Treeview(parent, columns=COLUMNS, show="headings", selectmode="browse")
        for col in COLUMNS:
            self.tree.heading(col, text=col)
        self.tree.column("名称", width=260)
        self.tree.column("类型", width=70)
        self.tree.column("大小", width=80)
        self.tree.column("修改时间", width=130)
        self.tree.column("位置", width=160)
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.bind("<Double-1>", lambda e: self.controller.on_double_click(e))
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.controller.on_select(e))
        self.tree.bind("<Button-3>", lambda e: self.controller.on_right_click(e))

    # ---- 列表操作 ----
    def clear(self):
        self.tree.delete(*self.tree.get_children())

    def add_item(self, full, name, is_dir, size, mtime, location):
        icon = "📁 " if is_dir else "📄 "
        self.tree.insert("", "end", iid=full, values=(
            icon + name,
            "文件夹" if is_dir else "文件",
            size, mtime, location,
        ))

    # ---- 选择/命中 ----
    def get_selected(self):
        sel = self.tree.selection()
        return sel[0] if sel else None

    def set_selection(self, iid):
        self.tree.selection_set(iid)

    def identify_row(self, y):
        return self.tree.identify_row(y)
