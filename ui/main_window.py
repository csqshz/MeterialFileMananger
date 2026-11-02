# -*- coding: utf-8 -*-
"""主窗口：控制器，协调工具栏、文件列表、功能面板与右键菜单。"""
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from config import BASE_DIR, LINK_SUFFIX, APP_TITLE, WINDOW_SIZE
from core import filesystem as fs
from core import linkfile

from ui.toolbar import Toolbar
from ui.file_list import FileList
from ui.side_panel import SidePanel
from ui.context_menu import ContextMenu

__all__ = ["MainWindow"]


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)

        self.current_path = BASE_DIR
        self.search_mode = False
        self.selected_path = None

        self._build_status_bar()
        self._build_layout()

        self.refresh()

    # ============================================================ 布局
    def _build_layout(self):
        self.toolbar = Toolbar(self.root, self)

        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        left = ttk.Frame(paned)
        self.file_list = FileList(left, self)
        paned.add(left, weight=3)

        right = ttk.Frame(paned)
        self.side_panel = SidePanel(right, self)
        paned.add(right, weight=1)

        self.context_menu = ContextMenu(self.root)

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(
            fill="x", side="bottom")

    # ============================================================ 列表刷新
    def refresh(self):
        self.file_list.clear()
        self.search_mode = False
        self.toolbar.set_path(self.current_path)
        try:
            dirs, files = fs.list_directory(self.current_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法访问目录:\n{e}")
            return
        for name in dirs + files:
            self._add(full=os.path.join(self.current_path, name))
        self.side_panel.show_empty("在左侧选择一个文件或文件夹查看功能菜单。")
        self.status(f"当前目录: {self.current_path}")

    def _add(self, full):
        name = os.path.basename(full)
        is_dir = os.path.isdir(full)
        try:
            st = os.stat(full)
            size = "" if is_dir else fs.format_size(st.st_size)
            mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
        except Exception:
            size, mtime = "", ""
        location = fs.relative_location(full, BASE_DIR)
        self.file_list.add_item(full, name, is_dir, size, mtime, location)

    # ============================================================ 导航
    def go_up(self):
        if os.path.abspath(self.current_path) != os.path.abspath(BASE_DIR):
            self.current_path = os.path.dirname(self.current_path)
            self.refresh()

    def goto_path(self, p):
        if os.path.isdir(p):
            self.current_path = os.path.abspath(p)
            self.refresh()
        else:
            messagebox.showerror("错误", "路径不存在或不是文件夹")

    # ============================================================ 搜索
    def do_search(self):
        q = self.toolbar.get_search()
        if not q.strip():
            self.refresh()
            return
        self.file_list.clear()
        self.search_mode = True
        self.toolbar.set_path(f"搜索结果: “{q}”  (范围: {BASE_DIR})")
        results = fs.search(BASE_DIR, q)
        for full in results:
            self._add(full)
        self.side_panel.show_empty("在左侧选择一个文件或文件夹查看功能菜单。")
        self.status(f"搜索到 {len(results)} 个结果")

    def clear_search(self):
        self.toolbar.clear_search()
        self.refresh()

    # ============================================================ 交互事件
    def on_select(self, event):
        full = self.file_list.get_selected()
        if not full:
            return
        self.selected_path = full
        self.side_panel.show(full)

    def on_double_click(self, event):
        full = self.file_list.get_selected()
        if not full:
            return
        if os.path.isdir(full):
            self.current_path = full
            if self.search_mode:
                self.clear_search()
            else:
                self.refresh()
        else:
            self.open_path(full)

    def on_right_click(self, event):
        iid = self.file_list.identify_row(event.y)
        if not iid:
            return
        self.file_list.set_selection(iid)
        self.selected_path = iid
        full = iid
        is_dir = os.path.isdir(full)
        items = [
            ("打开", lambda: self.open_path(full)),
            ("打开所在的文件夹", lambda: self.reveal(full)),
            ("复制路径", lambda: self.copy_path(full)),
            ("重命名", lambda: self.rename_file(full)),
            "---",
            ("刷新列表", self.refresh),
        ]
        if is_dir:
            items.insert(2, ("进入此文件夹", lambda: self._enter_dir(full)))
        self.context_menu.popup(event, items)

    def _enter_dir(self, full):
        self.current_path = full
        self.clear_search() if self.search_mode else self.refresh()

    # ============================================================ 操作实现
    def open_path(self, full):
        try:
            fs.open_path(full)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开:\n{e}")

    def reveal(self, full):
        try:
            fs.reveal_in_explorer(full)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开资源管理器:\n{e}")

    def copy_path(self, full):
        self.root.clipboard_clear()
        self.root.clipboard_append(full)
        self.status("已复制路径到剪贴板")

    def rename_file(self, full):
        old = os.path.basename(full)
        new = simpledialog.askstring("重命名", "请输入新文件名:", initialvalue=old)
        if not new or new == old:
            return
        try:
            fs.rename_file(full, new)
            self.refresh()
            self.status(f"已重命名为: {new}")
        except Exception as e:
            messagebox.showerror("错误", f"重命名失败:\n{e}")

    # ============================================================ 硬链接功能
    def toggle_hardlink(self, full):
        name = os.path.basename(full)
        if self.side_panel.chk_var.get():
            if not linkfile.is_hardlink(name):
                base = name[:-4] if name.lower().endswith(".txt") else name
                newname = base + LINK_SUFFIX
                newpath = os.path.join(os.path.dirname(full), newname)
                try:
                    fs.rename_file(full, newname)
                    linkfile.write_target(newpath, "")
                    self.selected_path = newpath
                    self.refresh()
                    self.status(f"已启用硬链接功能，重命名为: {newname}")
                except Exception as e:
                    messagebox.showerror("错误", f"启用硬链接失败:\n{e}")
                    self.side_panel.chk_var.set(False)
                    return
        # 重新渲染面板
        self.side_panel.show(full)

    def save_link(self, full, target):
        target = (target or "").strip()
        try:
            linkfile.write_target(full, target)
            self.status(f"已保存关联: {target if target else '(空)'}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败:\n{e}")

    def browse_mother(self, full):
        path = filedialog.askopenfilename(title="选择母本文件", initialdir=BASE_DIR)
        if path:
            self.side_panel.link_var.set(path)
            linkfile.write_target(full, path)
            self.status(f"已关联母本文件: {path}")

    def open_mother(self, full):
        target = linkfile.read_target(full)
        if target and os.path.exists(target):
            self.open_path(target)
        else:
            messagebox.showwarning("提示", "母本文件不存在或关联地址无效。")

    # ============================================================ 状态
    def status(self, msg):
        self.status_var.set(msg)
