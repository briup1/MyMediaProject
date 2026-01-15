#!/usr/bin/env python3
"""
Qwen-Image 图片生成脚本

使用通义千问Qwen-Image API生成图片。

使用方法：
    python generate_image.py --prompt "一只可爱的猫" --output image_01.jpg

环境变量：
    DASHSCOPE_API_KEY: 通义千问API密钥（必需）
    DASHSCOPE_API_URL: API端点（可选，默认北京）
"""

import argparse
import json
import os
import sys
import time
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载插件根目录下的 .env 文件
plugin_root = Path(__file__).parent.parent
load_dotenv(plugin_root / ".env")


# API配置
DEFAULT_API_URL = "https://dashscope.aliyuncs.com/api/v1"
IMAGE_GENERATION_ENDPOINT = "/services/aigc/multimodal-generation/generation"


def generate_image(
    prompt: str,
    size: str = "1328*1328",
    negative_prompt: str = "",
    prompt_extend: bool = True,
    watermark: bool = False
) -> Optional[dict]:
    """
    调用Qwen-Image API生成图片

    Args:
        prompt: 图片提示词
        size: 图片尺寸，默认1328*1328 (1:1)
        negative_prompt: 反向提示词
        prompt_extend: 是否智能改写提示词
        watermark: 是否添加水印

    Returns:
        API响应结果，包含图片URL
    """
    # 获取API配置
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 DASHSCOPE_API_KEY 环境变量", file=sys.stderr)
        print("获取API Key: https://help.aliyun.com/zh/model-studio/get-api-key", file=sys.stderr)
        return None

    api_url = os.getenv("DASHSCOPE_API_URL", DEFAULT_API_URL)
    url = api_url + IMAGE_GENERATION_ENDPOINT

    # 构建请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "qwen-image-plus",
        "input": {
            "messages": [{
                "role": "user",
                "content": [{"text": prompt}]
            }]
        },
        "parameters": {
            "size": size,
            "negative_prompt": negative_prompt,
            "prompt_extend": prompt_extend,
            "watermark": watermark
        }
    }

    try:
        print(f"🎨 正在生成图片...")
        print(f"   提示词: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print(f"   尺寸: {size}")

        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"❌ API调用失败: HTTP {response.status_code}", file=sys.stderr)
            print(f"   {response.text}", file=sys.stderr)
            return None

    except requests.Timeout:
        print("❌ 请求超时", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ 发生错误: {e}", file=sys.stderr)
        return None


def download_image(url: str, output_path: Path) -> bool:
    """
    下载生成的图片

    Args:
        url: 图片URL
        output_path: 输出文件路径

    Returns:
        是否下载成功
    """
    try:
        print(f"📥 正在下载图片...")
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存图片
            with open(output_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ 图片已保存: {output_path}")
            print(f"   文件大小: {len(response.content) / 1024:.1f} KB")
            return True
        else:
            print(f"❌ 下载失败: HTTP {response.status_code}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"❌ 下载失败: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="使用Qwen-Image生成图片")
    parser.add_argument("--prompt", "-p", required=True, help="图片提示词")
    parser.add_argument("--output", "-o", required=True, help="输出文件路径")
    parser.add_argument("--size", "-s", default="1328*1323",
                       choices=["1664*928", "1472*1140", "1328*1328", "1140*1472", "928*1664"],
                       help="图片尺寸 (默认: 1328*1328)")
    parser.add_argument("--negative-prompt", help="反向提示词")
    parser.add_argument("--no-prompt-extend", action="store_true",
                       help="禁用提示词智能改写")
    parser.add_argument("--watermark", action="store_true",
                       help="添加水印")
    parser.add_argument("--url-only", action="store_true",
                       help="仅输出图片URL，不下载")

    args = parser.parse_args()

    # 生成图片
    result = generate_image(
        prompt=args.prompt,
        size=args.size,
        negative_prompt=args.negative_prompt or "",
        prompt_extend=not args.no_prompt_extend,
        watermark=args.watermark
    )

    if not result:
        sys.exit(1)

    # 解析结果
    try:
        choices = result.get("output", {}).get("choices", [])
        if not choices:
            print("❌ API返回结果为空", file=sys.stderr)
            sys.exit(1)

        content = choices[0].get("message", {}).get("content", [])
        image_url = None

        for item in content:
            if "image" in item:
                image_url = item["image"]
                break

        if not image_url:
            print("❌ 未找到图片URL", file=sys.stderr)
            sys.exit(1)

        # 输出结果
        if args.url_only:
            print(image_url)
        else:
            # 下载图片
            output_path = Path(args.output)
            success = download_image(image_url, output_path)

            if not success:
                print(f"\n⚠️  自动下载失败，图片URL（24小时有效）：")
                print(image_url)
                sys.exit(1)

            # 输出元数据
            print(f"\n📊 生成信息:")
            print(f"   模型: qwen-image-plus")
            print(f"   尺寸: {result.get('usage', {}).get('width')}x{result.get('usage', {}).get('height')}")
            print(f"   任务ID: {result.get('request_id')}")

    except Exception as e:
        print(f"❌ 处理结果时发生错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
