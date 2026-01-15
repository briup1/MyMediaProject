#!/usr/bin/env python3
"""
插件路径解析辅助模块

提供统一的路径解析功能，确保在全局安装和本地安装时都能正确找到插件资源。
"""

import os
from pathlib import Path


def get_plugin_root() -> Path:
    """
    获取插件根目录路径

    优先使用 CLAUDE_PLUGIN_ROOT 环境变量（Claude Code设置），
    否则基于当前文件位置自动推断。

    Returns:
        Path: 插件根目录的绝对路径
    """
    # 优先使用环境变量
    env_plugin_root = os.getenv("CLAUDE_PLUGIN_ROOT")
    if env_plugin_root:
        return Path(env_plugin_root)

    # 回退：基于本文件位置推断
    # 本文件在 scripts/ 目录下，所以需要向上两级
    current_file = Path(__file__).resolve()
    return current_file.parent.parent


def get_script_path(script_name: str) -> Path:
    """
    获取脚本的绝对路径

    Args:
        script_name: 脚本文件名（如 'fetch_trending.py'）

    Returns:
        Path: 脚本的绝对路径
    """
    return get_plugin_root() / "scripts" / script_name


def get_persona_path(persona_name: str) -> Path:
    """
    获取人设文件的绝对路径

    Args:
        persona_name: 人设文件名（如 '示例人设.md'）

    Returns:
        Path: 人设文件的绝对路径
    """
    return get_plugin_root() / "personas" / persona_name


def get_personas_dir() -> Path:
    """
    获取人设目录的绝对路径

    Returns:
        Path: personas 目录的绝对路径
    """
    return get_plugin_root() / "personas"


def get_scripts_dir() -> Path:
    """
    获取脚本目录的绝对路径

    Returns:
        Path: scripts 目录的绝对路径
    """
    return get_plugin_root() / "scripts"


def main():
    """测试路径解析功能"""
    print("=== 插件路径测试 ===")
    print(f"CLAUDE_PLUGIN_ROOT: {os.getenv('CLAUDE_PLUGIN_ROOT', '未设置')}")
    print(f"\n推断的插件根目录: {get_plugin_root()}")
    print(f"脚本目录: {get_scripts_dir()}")
    print(f"人设目录: {get_personas_dir()}")

    # 测试具体文件路径
    print(f"\n示例路径:")
    print(f"  fetch_trending.py: {get_script_path('fetch_trending.py')}")
    print(f"  generate_image.py: {get_script_path('generate_image.py')}")
    print(f"  示例人设.md: {get_persona_path('示例人设.md')}")

    # 验证路径是否存在
    for path in [get_plugin_root(), get_scripts_dir(), get_personas_dir()]:
        status = "✓" if path.exists() else "✗"
        print(f"  {status} {path}: {'存在' if path.exists() else '不存在'}")


if __name__ == "__main__":
    main()
