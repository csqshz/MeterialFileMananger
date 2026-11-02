# -*- coding: utf-8 -*-
"""顶部工具栏：目录导航 + 搜索。"""
import tkinter as tk
from tkinter import ttk

__all__ = ["Toolbar"]


class Toolbar:
    """导航与搜索栏，向控制器回传事件。"""

    def __init__(self, parent, controller):
        self.controller = controller
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=6, pady=6)

        # 第一行：位置栏
        row1 = ttk.Frame(frame)
        row1.pack(fill="x", pady=(0, 4))
        ttk.Button(row1, text="↑", width=3, command=self.controller.go_up).pack(side="left")
        ttk.Label(row1, text="位置:").pack(side="left")
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(row1, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=3)
        self.path_entry.bind("<Return>", lambda e: self.controller.goto_path(self.path_var.get()))
        ttk.Button(row1, text="转到",
                   command=lambda: self.controller.goto_path(self.path_var.get())).pack(side="left")

        # 第二行：搜索栏
        row2 = ttk.Frame(frame)
        row2.pack(fill="x")
        ttk.Label(row2, text="搜索:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(row2, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=3)
        self.search_entry.bind("<Return>", lambda e: self.controller.do_search())
        ttk.Button(row2, text="搜索", command=self.controller.do_search).pack(side="left")
        ttk.Button(row2, text="清除", command=self.controller.clear_search).pack(side="left")

    # ---- 外部控制 ----
    def set_path(self, path):
        self.path_var.set(path)

    def get_search(self):
        return self.search_var.get()

    def clear_search(self):
        self.search_var.set("")
