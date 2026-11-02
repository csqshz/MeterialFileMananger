# -*- coding: utf-8 -*-
"""
资料管理器 / 模块文件管理器 —— 程序入口
管理 "E:\项目资料" 下的资料：搜索、浏览、右键菜单、硬链接关联。

运行：python main.py  (仅依赖 Python 标准库)
"""
import os
import tkinter as tk

from config import BASE_DIR
from ui.main_window import MainWindow

if __name__ == "__main__":
    # 根目录不存在时尝试创建，保证程序可启动
    if not os.path.isdir(BASE_DIR):
        try:
            os.makedirs(BASE_DIR, exist_ok=True)
        except Exception:
            pass

    root = tk.Tk()
    MainWindow(root)
    root.mainloop()
