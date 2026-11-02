# -*- coding: utf-8 -*-
"""硬链接文件（xxx-硬链接.txt）的判断与读写逻辑。"""
from config import LINK_SUFFIX

__all__ = ["is_hardlink", "read_target", "write_target"]


def is_hardlink(name):
    """判断文件名是否符合硬链接文件格式：xxx-硬链接.txt。"""
    return name.endswith(LINK_SUFFIX)


def read_target(path):
    """读取硬链接文件记录的母本文件地址（目录+文件名）。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""


def write_target(path, target):
    """把母本文件地址写入硬链接文件并保存。"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(target)
