# -*- coding: utf-8 -*-
"""右侧功能菜单面板：展示选中项的功能，并支持硬链接关联编辑。"""
import os
import tkinter as tk
from tkinter import ttk

from core import linkfile

__all__ = ["SidePanel"]


class SidePanel:
    """渲染选中文件/文件夹的功能菜单。硬链接编辑区会回调控制器保存。"""

    def __init__(self, parent, controller):
        self.controller = controller
        self.link_var = tk.StringVar()
        self.chk_var = tk.BooleanVar()

        # 可滚动容器
        canvas = tk.Canvas(parent, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        rsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        rsb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=rsb.set)

        self.panel = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.panel, anchor="nw")
        self.panel.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # -------------------------------------------------- 公共接口
    def show_empty(self, msg):
        self._clear()
        ttk.Label(self.panel, text=msg, wraplength=280).pack(anchor="w", padx=8, pady=10)

    def show(self, full):
        """根据选中项渲染对应功能菜单。"""
        self._clear()
        name = os.path.basename(full)
        is_dir = os.path.isdir(full)
        is_file = os.path.isfile(full)

        ttk.Label(self.panel, text="功能菜单", font=("", 11, "bold")).pack(anchor="w", padx=8, pady=(8, 4))
        ttk.Label(self.panel, text=f"名称: {name}", wraplength=280).pack(anchor="w", padx=8)
        ttk.Label(self.panel, text=f"类型: {'文件夹' if is_dir else '文件'}").pack(anchor="w", padx=8)
        ttk.Label(self.panel, text=f"路径: {full}", wraplength=280).pack(anchor="w", padx=8, pady=(0, 6))

        if is_dir:
            self._dir_actions(full)
            return

        # 文件通用功能
        self._file_actions(full)

        # 仅对 txt 文件显示“硬链接”勾选功能
        if is_file and name.lower().endswith(".txt"):
            ttk.Separator(self.panel).pack(fill="x", padx=8, pady=8)
            self.chk_var.set(linkfile.is_hardlink(name))
            ttk.Checkbutton(self.panel, text="硬链接功能", variable=self.chk_var,
                            command=lambda: self.controller.toggle_hardlink(full)).pack(anchor="w", padx=8)

        # 若是硬链接文件，展示关联编辑区
        if is_file and linkfile.is_hardlink(name):
            self._hardlink_editor(full)

    # -------------------------------------------------- 各区块渲染
    def _dir_actions(self, full):
        ttk.Button(self.panel, text="进入此文件夹",
                   command=lambda: self.controller.open_path(full)).pack(anchor="w", padx=8, pady=2, fill="x")
        ttk.Button(self.panel, text="在资源管理器中打开",
                   command=lambda: self.controller.reveal(full)).pack(anchor="w", padx=8, pady=2, fill="x")

    def _file_actions(self, full):
        ttk.Button(self.panel, text="打开文件",
                   command=lambda: self.controller.open_path(full)).pack(anchor="w", padx=8, pady=2, fill="x")
        ttk.Button(self.panel, text="打开所在的文件夹",
                   command=lambda: self.controller.reveal(full)).pack(anchor="w", padx=8, pady=2, fill="x")
        ttk.Button(self.panel, text="修改文件名",
                   command=lambda: self.controller.rename_file(full)).pack(anchor="w", padx=8, pady=2, fill="x")

    def _hardlink_editor(self, full):
        ttk.Separator(self.panel).pack(fill="x", padx=8, pady=8)
        ttk.Label(self.panel, text="硬链接关联设置", font=("", 10, "bold")).pack(anchor="w", padx=8)

        target = linkfile.read_target(full)
        ttk.Label(self.panel, text="关联的母本文件地址:").pack(anchor="w", padx=8, pady=(4, 0))
        self.link_var.set(target)
        entry = ttk.Entry(self.panel, textvariable=self.link_var)
        entry.pack(fill="x", padx=8, pady=3)
        # 失焦或回车即自动保存
        entry.bind("<FocusOut>", lambda e: self.controller.save_link(full, self.link_var.get()))
        entry.bind("<Return>", lambda e: self.controller.save_link(full, self.link_var.get()))

        bf = ttk.Frame(self.panel)
        bf.pack(fill="x", padx=8, pady=3)
        ttk.Button(bf, text="保存", command=lambda: self.controller.save_link(full, self.link_var.get())).pack(
            side="left", padx=(0, 4))
        ttk.Button(bf, text="浏览母本文件",
                   command=lambda: self.controller.browse_mother(full)).pack(side="left", padx=(0, 4))
        ttk.Button(bf, text="打开母本文件", command=lambda: self.controller.open_mother(full)).pack(side="left")

        ttk.Label(self.panel, text="提示: 修改地址后失焦或回车即可自动保存到硬链接文件。").pack(
            anchor="w", padx=8, pady=(6, 0), wraplength=280)

    # -------------------------------------------------- 内部工具
    def _clear(self):
        for w in self.panel.winfo_children():
            w.destroy()
