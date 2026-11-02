# -*- coding: utf-8 -*-
"""右键上下文菜单。"""
import tkinter as tk
from tkinter import Menu

__all__ = ["ContextMenu"]


class ContextMenu:
    """根据传入的菜单项动态弹出右键菜单。"""

    def __init__(self, root):
        self.root = root

    def popup(self, event, items):
        """
        items: 菜单项列表，元素为 (label, command) 或字符串 "---" 表示分隔线。
        """
        menu = Menu(self.root, tearoff=0)
        for item in items:
            if item == "---":
                menu.add_separator()
            else:
                label, command = item
                menu.add_command(label=label, command=command)
        menu.tk_popup(event.x_root, event.y_root)
