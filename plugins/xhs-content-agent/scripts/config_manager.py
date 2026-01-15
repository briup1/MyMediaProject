#!/usr/bin/env python3
"""
用户配置管理脚本

用于读取和保存用户配置，减少重复交互。
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


# 配置文件路径
CONFIG_FILE = Path(os.getenv("CLAUDE_PLUGIN_ROOT", ".")) / ".user_config.json"
CONFIG_TEMPLATE = {
    "persona": None,
    "default_image_style": "warm_healing",
    "account": None,
    "default_image_count": 3,
    "auto_optimize": True,
    "auto_publish": False,
    "created_at": None
}


def ensure_config_exists() -> Path:
    """确保配置文件存在"""
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(CONFIG_TEMPLATE.copy(), f, ensure_ascii=False, indent=2)
        print(f"✅ 已创建配置文件: {CONFIG_FILE}")
    return CONFIG_FILE


def load_config() -> Dict:
    """加载用户配置"""
    ensure_config_exists()
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


def save_config(config: Dict) -> None:
    """保存用户配置"""
    ensure_config_exists()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_persona() -> Optional[str]:
    """获取当前人设"""
    config = load_config()
    return config.get("persona")


def set_persona(persona_name: str) -> None:
    """设置人设"""
    config = load_config()
    config["persona"] = persona_name
    save_config(config)
    print(f"✅ 已设置人设: {persona_name}")


def get_default_image_style() -> str:
    """获取默认图片风格"""
    config = load_config()
    return config.get("default_image_style", "warm_healing")


def set_default_image_style(style: str) -> None:
    """设置默认图片风格"""
    config = load_config()
    config["default_image_style"] = style
    save_config(config)
    print(f"✅ 已设置默认图片风格: {style}")


def get_account() -> Optional[str]:
    """获取当前账号"""
    config = load_config()
    return config.get("account")


def set_account(account_name: str) -> None:
    """设置账号"""
    config = load_config()
    config["account"] = account_name
    save_config(config)
    print(f"✅ 已设置账号: {account_name}")


def get_default_image_count() -> int:
    """获取默认图片数量"""
    config = load_config()
    return config.get("default_image_count", 3)


def set_default_image_count(count: int) -> None:
    """设置默认图片数量"""
    config = load_config()
    config["default_image_count"] = count
    save_config(config)
    print(f"✅ 已设置默认图片数量: {count}")


def is_auto_optimize() -> bool:
    """是否自动优化"""
    config = load_config()
    return config.get("auto_optimize", True)


def set_auto_optimize(enabled: bool) -> None:
    """设置是否自动优化"""
    config = load_config()
    config["auto_optimize"] = enabled
    save_config(config)
    status = "启用" if enabled else "禁用"
    print(f"✅ 已{status}自动优化")


def is_auto_publish() -> bool:
    """是否自动发布"""
    config = load_config()
    return config.get("auto_publish", False)


def set_auto_publish(enabled: bool) -> None:
    """设置是否自动发布"""
    config = load_config()
    config["auto_publish"] = enabled
    save_config(config)
    status = "启用" if enabled else "禁用"
    print(f"✅ 已{status}自动发布")


def get_config_summary() -> str:
    """获取配置摘要"""
    config = load_config()
    summary = [
        "## 当前配置",
        f"- 人设: {config.get('persona', '未设置')}",
        f"- 默认图片风格: {config.get('default_image_style', 'warm_healing')}",
        f"- 账号: {config.get('account', '未设置')}",
        f"- 默认图片数量: {config.get('default_image_count', 3)}",
        f"- 自动优化: {'是' if config.get('auto_optimize', True) else '否'}",
        f"- 自动发布: {'是' if config.get('auto_publish', False) else '否'}"
    ]
    return "\n".join(summary)


def reset_config() -> None:
    """重置配置"""
    ensure_config_exists()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(CONFIG_TEMPLATE.copy(), f, ensure_ascii=False, indent=2)
    print(f"✅ 已重置配置文件")


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="用户配置管理")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # show 命令
    subparsers.add_parser('show', help='显示当前配置')

    # set 命令
    set_parser = subparsers.add_parser('set', help='设置配置项')
    set_parser.add_argument('key', help='配置项名称')
    set_parser.add_argument('value', help='配置项值')

    # reset 命令
    subparsers.add_parser('reset', help='重置配置')

    args = parser.parse_args()

    if args.command == 'show':
        print(get_config_summary())
    elif args.command == 'set':
        if args.key == 'persona':
            set_persona(args.value)
        elif args.key == 'style':
            set_default_image_style(args.value)
        elif args.key == 'account':
            set_account(args.value)
        elif args.key == 'image_count':
            set_default_image_count(int(args.value))
        elif args.key == 'auto_optimize':
            set_auto_optimize(args.value.lower() in ['true', 'yes', '1'])
        elif args.key == 'auto_publish':
            set_auto_publish(args.value.lower() in ['true', 'yes', '1'])
        else:
            print(f"❌ 未知的配置项: {args.key}")
    elif args.command == 'reset':
        reset_config()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
