# -*- coding: utf-8 -*-
"""文件系统相关的纯逻辑操作（不依赖 tkinter）。"""
import os
import subprocess

__all__ = [
    "list_directory",
    "search",
    "open_path",
    "reveal_in_explorer",
    "rename_file",
    "format_size",
    "relative_location",
]


def list_directory(path):
    """列举目录内容，返回排序后的 (文件夹名列表, 文件名列表)。"""
    dirs, files = [], []
    for name in os.listdir(path):
        full = os.path.join(path, name)
        (dirs if os.path.isdir(full) else files).append(name)
    dirs.sort(key=str.lower)
    files.sort(key=str.lower)
    return dirs, files


def search(base, query):
    """在 base 目录下递归搜索文件名包含 query 的项，返回完整路径列表。"""
    query = query.strip().lower()
    results = []
    for root, dirs, files in os.walk(base):
        for name in list(dirs) + list(files):
            if query in name.lower():
                results.append(os.path.join(root, name))
    results.sort()
    return results


def open_path(path):
    """用系统默认程序打开文件或文件夹。"""
    os.startfile(os.path.normpath(path))


def reveal_in_explorer(path):
    """在资源管理器中定位并选中该项。"""
    subprocess.run(f'explorer /select,"{os.path.normpath(path)}"', shell=True)


def rename_file(full, new_name):
    """重命名文件/文件夹，返回新路径。"""
    new_path = os.path.join(os.path.dirname(full), new_name)
    os.rename(full, new_path)
    return new_path


def format_size(n):
    """将字节数格式化为可读字符串。"""
    if n < 0:
        return ""
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def relative_location(full, base):
    """返回相对 base 的所在位置描述。"""
    try:
        rel = os.path.relpath(os.path.dirname(full), base)
        return "(根目录)" if rel == "." else rel
    except Exception:
        return ""
