#!/usr/bin/env python3
"""
热榜数据获取脚本

使用今日热榜 (rebang.today) 的 jina.ai Reader API 获取实时热榜数据。

支持的平台：
- xhs: 小红书
- ne-news: 网易新闻
- zhihu: 知乎
- weibo: 微博
- douyin: 抖音
- bilibili: 哔哩哔哩

使用方法：
    python fetch_trending.py --platform xhs
    python fetch_trending.py --platform ne-news --limit 20
"""

import argparse
import json
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import unquote
import requests


# 今日热榜 jina.ai Reader API 端点
REBANG_API_BASE = "https://r.jina.ai/rebang.today"

# 支持的平台映射
PLATFORMS = {
    "xhs": "xiaohongshu",      # 小红书
    "ne-news": "ne-news",      # 网易新闻
    "zhihu": "zhihu",          # 知乎
    "weibo": "weibo",          # 微博
    "douyin": "douyin",        # 抖音
    "bilibili": "bilibili",    # 哔哩哔哩
    "36kr": "36kr",            # 36氪
    "toutiao": "toutiao",      # 今日头条
    "ithome": "ithome",        # IT之家
}


def fetch_rebang(platform: str, limit: int = 50) -> List[Dict]:
    """
    从今日热榜获取平台热榜数据

    Args:
        platform: 平台代码 (xhs, ne-news, zhihu等)
        limit: 返回的最大数量

    Returns:
        热榜数据列表，每项包含：
        - rank: 排名
        - title: 标题
        - heat: 热度值
        - url: 链接
        - trend: 趋势 (hot/new/normal)
    """
    # 获取平台对应的 tab 参数
    tab = PLATFORMS.get(platform)
    if not tab:
        print(f"❌ 错误：不支持的平台 '{platform}'", file=sys.stderr)
        print(f"   支持的平台：{', '.join(PLATFORMS.keys())}", file=sys.stderr)
        return []

    # 构建 API URL
    url = f"{REBANG_API_BASE}/?tab={tab}"

    try:
        print(f"📡 正在获取 {platform} 热榜数据...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # 解析返回的内容
        content = response.text

        # 解析热榜数据
        trending_data = parse_rebang_content(content, platform, limit)

        print(f"📊 解析到 {len(trending_data)} 条数据")

        return trending_data

    except requests.RequestException as e:
        print(f"❌ 获取热榜数据失败: {e}", file=sys.stderr)
        return []


def parse_rebang_content(content: str, platform: str, limit: int) -> List[Dict]:
    """
    解析今日热榜返回的 Markdown 内容

    小红书格式：
    *   1
    [棋圣聂卫平病逝 新 ----------](https://www.xiaohongshu.com/search_result?keyword=... "棋圣聂卫平病逝")
    948.1w

    网易新闻格式：
    * [图片](url) [标题](url "title")描述
    来源 跟贴数

    Args:
        content: 返回的文本内容
        platform: 平台代码
        limit: 最大返回数量

    Returns:
        解析后的热榜数据列表
    """
    # 根据平台选择不同的解析方式
    if platform == "ne-news":
        return parse_ne_news_format(content, limit)
    elif platform == "xhs":
        return parse_xhs_format(content, limit)
    else:
        # 默认使用小红书格式
        return parse_xhs_format(content, limit)


def parse_xhs_format(content: str, limit: int) -> List[Dict]:
    """
    解析小红书格式热榜
    """
    trending_list = []

    # 匹配模式：
    # *   数字\n
    # [标题... 标记](url "title")\n
    # 热度值
    pattern = r'\*\s+(\d+)\s*\n\[([^\]]+)\]\(([^)]+)\)\s*\n\s*([\d.]+[w千万]?)'

    matches = re.findall(pattern, content)

    for match in matches:
        if len(trending_list) >= limit:
            break

        rank = int(match[0])
        title_with_flag = match[1]
        url = match[2]
        heat_str = match[3]

        # 解析标题和趋势标记
        title = title_with_flag.strip()

        # 确定趋势
        trend = "normal"
        if " 新 " in title or title.endswith(" 新"):
            trend = "new"
            title = re.sub(r'\s+新\s*-+$', '', title)
            title = re.sub(r'\s+新$', '', title)
        elif " 热 " in title or title.endswith(" 热"):
            trend = "hot"
            title = re.sub(r'\s+热\s*-+$', '', title)
            title = re.sub(r'\s+热$', '', title)

        # 清理标题末尾的横线
        title = re.sub(r'-+$', '', title).strip()

        # URL解码（如果需要）
        try:
            if 'keyword=' in url:
                keyword_match = re.search(r'keyword=([^&\s]+)', url)
                if keyword_match:
                    encoded_title = keyword_match.group(1)
                    decoded_title = unquote(encoded_title)
                    title = decoded_title
        except:
            pass

        # 解析热度值
        heat = parse_heat_value(heat_str)

        trending_list.append({
            "rank": rank,
            "title": title,
            "url": url.strip(),
            "heat": heat,
            "trend": trend
        })

    return trending_list


def parse_ne_news_format(content: str, limit: int) -> List[Dict]:
    """
    解析网易新闻格式热榜

    网易新闻格式较复杂，包含图片链接和多个行
    使用简化的解析逻辑：提取所有新闻标题链接和跟贴数
    """
    trending_list = []

    # 提取所有标题链接和跟贴数
    # 1. 提取所有 [标题](url) 模式
    # 2. 提取所有 X人跟贴 模式
    # 3. 配对它们

    title_pattern = r'\[([^\]]+)\]\((https://c\.m\.163\.com/news/a/[^\)]+)\)'
    comment_pattern = r'(\d+)人跟贴'

    titles = re.findall(title_pattern, content)
    comments = re.findall(comment_pattern, content)

    # 配对标题和跟贴数（假设它们是按顺序对应的）
    for i, (title, url) in enumerate(titles):
        if len(trending_list) >= limit:
            break

        # 跳过纯图片链接
        if 'Image' in title or len(title) < 5:
            continue

        # 获取对应的跟贴数
        if i < len(comments):
            heat = int(comments[i])
        else:
            heat = 0

        # 清理标题中的多余横线
        title = re.sub(r'-+$', '', title).strip()

        trending_list.append({
            "rank": len(trending_list) + 1,
            "title": title,
            "url": url,
            "heat": heat,
            "trend": "normal"
        })

    return trending_list


def parse_heat_value(heat_str: str) -> Optional[int]:
    """
    解析热度字符串为数值

    Args:
        heat_str: 热度字符串，如 "948.1w", "707.2w", "400w"

    Returns:
        热度数值
    """
    if not heat_str:
        return None

    heat_str = heat_str.strip().lower()

    # 处理 "w" (万) 单位
    if 'w' in heat_str:
        try:
            value = float(heat_str.replace('w', ''))
            return int(value * 10000)
        except ValueError:
            pass

    # 处理 "千万" 单位
    if '千万' in heat_str:
        try:
            value = float(heat_str.replace('千万', ''))
            return int(value * 10000000)
        except ValueError:
            pass

    # 纯数字
    try:
        return int(float(heat_str))
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="获取各平台实时热榜数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
支持的平台：
  xhs       小红书
  ne-news   网易新闻
  zhihu     知乎
  weibo     微博
  douyin    抖音
  bilibili  哔哩哔哩
  36kr      36氪
  toutiao   今日头条
  ithome    IT之家

示例：
  %(prog)s --platform xhs
  %(prog)s --platform ne-news --limit 20
  %(prog)s -p zhihu -o trending.json
        """
    )

    parser.add_argument(
        "--platform", "-p",
        required=True,
        choices=list(PLATFORMS.keys()),
        help="平台代码"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=50,
        help="返回的最大数量 (默认: 50)"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出 JSON 文件路径"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="美化输出格式"
    )

    args = parser.parse_args()

    # 获取热榜数据
    trending_data = fetch_rebang(args.platform, args.limit)

    if not trending_data:
        print(f"❌ 未获取到热榜数据", file=sys.stderr)
        sys.exit(1)

    # 构建结果
    result = {
        "platform": args.platform,
        "platform_name": PLATFORMS[args.platform],
        "fetch_time": datetime.now().isoformat(),
        "count": len(trending_data),
        "data": trending_data
    }

    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2 if args.pretty else None)
        print(f"✅ 数据已保存到 {args.output}")
        print(f"📊 共获取 {len(trending_data)} 条热榜数据")
    else:
        indent = 2 if args.pretty else None
        print(json.dumps(result, ensure_ascii=False, indent=indent))


if __name__ == "__main__":
    main()
