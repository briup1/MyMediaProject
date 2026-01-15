#!/usr/bin/env python3
"""
小红书内容获取工具
使用requests和BeautifulSoup获取小红书链接内容
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.content_manager import ContentManager
from src.utils.download_images_from_urls import download_multiple_files
 
def extract_xhs_content(url):
    """
    提取小红书链接内容
    
    Args:
        url: 小红书链接（支持短链接和原始链接）
    
    Returns:
        dict: 包含标题、内容、图片URL等信息的字典
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        # 处理短链接重定向
        print(f"正在解析链接: {url}")
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=30)
        response.raise_for_status()
        
        # 获取最终重定向的URL
        final_url = response.url
        print(f"重定向到: {final_url}")
        
        # 解析小红书笔记ID
        note_id = extract_note_id(final_url)
        if not note_id:
            return {"error": "无法解析小红书笔记ID"}
        
        print(f"解析到笔记ID: {note_id}")
        
        # 获取页面内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title = extract_title(soup)
        
        # 提取内容
        content = extract_content(soup)
        
        # 提取图片URL
        image_urls = extract_image_urls(soup)
        
        # 提取标签
        tags = extract_tags(soup)
        
        # 提取作者信息
        author_info = extract_author_info(soup)
        
        result = {
            "note_id": note_id,
            "title": title,
            "content": content,
            "image_urls": image_urls,
            "tags": tags,
            "author": author_info,
            "url": final_url,
            "original_url": url,
            "extraction_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return result
        
    except requests.RequestException as e:
        return {"error": f"网络请求失败: {str(e)}"}
    except Exception as e:
        return {"error": f"解析失败: {str(e)}"}

def extract_note_id(url):
    """从URL中提取小红书笔记ID"""
    # 匹配小红书笔记URL模式
    patterns = [
        r'/explore/([a-f0-9]+)',  # 标准格式
        r'/discovery/item/([a-f0-9]+)',  # 发现页格式
        r'noteId=([a-f0-9]+)',  # 参数格式
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # 如果无法匹配，尝试从路径中提取
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    for part in path_parts:
        if len(part) >= 8 and re.match(r'^[a-f0-9]+$', part):
            return part
    
    return None

def extract_title(soup):
    """提取标题"""
    # 尝试多种选择器
    selectors = [
        'meta[property="og:title"]',
        'title',
        '.note-title',
        'h1',
        '.title'
    ]
    
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            title = element.get('content') or element.get_text(strip=True)
            if title and len(title) > 5:
                return title
    
    return "未找到标题"

def extract_content(soup):
    """提取内容"""
    # 尝试多种选择器
    selectors = [
        '.note-content',
        '.content',
        '.desc',
        'meta[property="og:description"]',
        'meta[name="description"]',
        'article'
    ]
    
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            content = element.get('content') or element.get_text(strip=True)
            if content and len(content) > 10:
                # 清理内容
                content = re.sub(r'\s+', ' ', content)
                return content.strip()
    
    return "未找到内容"

def extract_image_urls(soup):
    """提取图片URL"""
    image_urls = []
    
    # 首先尝试从JSON数据中提取图片（小红书常用方法）
    script_tags = soup.find_all('script')
    for script in script_tags:
        script_content = script.string
        if script_content and 'imageList' in script_content:
            # 尝试解析JSON数据
            import json
            import re
            
            # 查找JSON数据
            json_pattern = r'\{"imageList":\[.*?\]\}'
            matches = re.findall(json_pattern, script_content, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if 'imageList' in data:
                        for img_info in data['imageList']:
                            if isinstance(img_info, dict) and 'url' in img_info:
                                image_urls.append(img_info['url'])
                            elif isinstance(img_info, str):
                                image_urls.append(img_info)
                except:
                    pass
    
    # 尝试多种选择器
    selectors = [
        'img[src*="xiaohongshu"]',
        'img[src*="xhscdn"]',
        'img[src*="sns-img"]',
        '.note-image img',
        '.image img',
        '.content-image img',
        'img[alt*="小红书"]',
        'img[data-src*="xiaohongshu"]',
        'img[data-src*="xhscdn"]',
        'img[data-src*="sns-img"]',
        'img',  # 所有图片
        'div[style*="background-image"]'  # 背景图片
    ]
    
    for selector in selectors:
        images = soup.select(selector)
        for img in images:
            # 尝试多个属性
            for attr in ['src', 'data-src', 'data-original', 'original', 'url']:
                src = img.get(attr)
                if src and src.startswith(('http://', 'https://', '//')):
                    # 处理相对路径
                    if src.startswith('//'):
                        src = 'https:' + src
                    image_urls.append(src)
                    break  # 找到一个有效URL就停止
            
            # 检查背景图片
            style = img.get('style', '')
            if 'background-image' in style:
                import re
                bg_match = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
                if bg_match:
                    bg_url = bg_match.group(1)
                    if bg_url.startswith(('http://', 'https://', '//')):
                        if bg_url.startswith('//'):
                            bg_url = 'https:' + bg_url
                        image_urls.append(bg_url)
    
    # 去重并过滤无效URL
    unique_urls = []
    for url in set(image_urls):
        # 过滤掉可能不是图片的URL
        if any(keyword in url.lower() for keyword in ['xiaohongshu', 'xhscdn', 'sns-img', 'alicdn', 'cdn']):
            # 检查是否是图片URL（包含常见图片扩展名或图片关键词）
            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', 'image', 'img']):
                unique_urls.append(url)
    
    return unique_urls

def extract_tags(soup):
    """提取标签"""
    tags = []
    
    # 从内容中提取标签
    content = extract_content(soup)
    if content:
        hashtags = re.findall(r'#([^#\s]+)', content)
        tags.extend(hashtags)
    
    # 从meta标签中提取
    meta_keywords = soup.find('meta', {'name': 'keywords'})
    if meta_keywords:
        keywords = meta_keywords.get('content', '')
        if keywords:
            tags.extend([tag.strip() for tag in keywords.split(',') if tag.strip()])
    
    return list(set(tags))

def extract_author_info(soup):
    """提取作者信息"""
    # 尝试提取作者名
    selectors = [
        '.author-name',
        '.user-name',
        '.nickname',
        'meta[property="og:article:author"]'
    ]
    
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            author = element.get('content') or element.get_text(strip=True)
            if author:
                return author
    
    return "未知作者"

def save_xhs_content(content_data, account_name="AI知识账号", download_images=True):
    """
    保存小红书内容到项目目录
    
    Args:
        content_data: 提取的内容数据
        account_name: 账号名称
        download_images: 是否下载图片
    
    Returns:
        Path: 保存的目录路径
    """
    if "error" in content_data:
        print(f"❌ 保存失败: {content_data['error']}")
        return None
    
    # 创建内容管理器
    manager = ContentManager()
    
    # 生成帖子标题
    title = content_data.get('title', f"小红书笔记_{content_data.get('note_id', 'unknown')}")
    
    # 创建帖子目录
    post_dir = manager.create_post_directory(
        content_data.get('note_id', 'unknown'),
        title,
        account_name
    )
    
    print(f"📁 创建目录: {post_dir}")
    
    # 准备帖子信息
    post_info = {
        "title": title,
        "post_id": content_data.get('note_id', 'unknown'),
        "url": content_data.get('url', ''),
        "original_url": content_data.get('original_url', ''),
        "author": content_data.get('author', '未知作者'),
        "publish_time": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
        "tags": content_data.get('tags', []),
        "description": content_data.get('content', ''),
        "extraction_time": content_data.get('extraction_time', ''),
        "image_urls": content_data.get('image_urls', [])
    }
    
    # 保存帖子信息
    info_path = manager.save_post_info(post_dir, post_info)
    print(f"💾 保存帖子信息到: {info_path}")
    
    # 保存原始内容
    raw_content_path = post_dir / "raw_content.json"
    with open(raw_content_path, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, ensure_ascii=False, indent=2)
    print(f"📄 保存原始内容到: {raw_content_path}")
    
    # 保存为Markdown格式
    md_content = generate_markdown_content(content_data)
    md_path = post_dir / "content.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"📝 保存Markdown内容到: {md_path}")
    
    # 下载图片
    if download_images and content_data.get('image_urls'):

        image_urls = content_data.get('image_urls', [])
        if image_urls:
            print(f"\n📷 开始下载 {len(image_urls)} 张图片...")
            downloads_dir = post_dir / "downloads"
            results = download_multiple_files(image_urls, downloads_dir, "image_{:02d}")
            
            print(f"📊 图片下载完成:")
            print(f"   成功: {results['success']}/{results['total']}")
            print(f"   失败: {results['failed']}/{results['total']}")
            
            if results['failed_urls']:
                print("\n❌ 下载失败的URL:")
                for url in results['failed_urls']:
                    print(f"  - {url}")
        else:
            print("\nℹ️  未发现可下载的图片")
    
    return post_dir

def generate_markdown_content(content_data):
    """生成Markdown格式的内容"""
    lines = []
    
    # 标题
    lines.append(f"# {content_data.get('title', '小红书笔记')}")
    lines.append("")
    
    # 元信息
    lines.append("## 基本信息")
    lines.append(f"- **笔记ID**: {content_data.get('note_id', '未知')}")
    lines.append(f"- **作者**: {content_data.get('author', '未知作者')}")
    lines.append(f"- **提取时间**: {content_data.get('extraction_time', '未知')}")
    lines.append(f"- **原始链接**: {content_data.get('original_url', '')}")
    lines.append(f"- **重定向链接**: {content_data.get('url', '')}")
    lines.append("")
    
    # 内容
    lines.append("## 内容")
    content = content_data.get('content', '')
    if content:
        lines.append(content)
    else:
        lines.append("*内容为空*")
    lines.append("")
    
    # 标签
    tags = content_data.get('tags', [])
    if tags:
        lines.append("## 标签")
        lines.append(" ".join([f"#{tag}" for tag in tags]))
        lines.append("")
    
    # 图片信息
    image_urls = content_data.get('image_urls', [])
    if image_urls:
        lines.append("## 图片")
        lines.append(f"共发现 {len(image_urls)} 张图片")
        lines.append("")
        
        # 添加已下载图片的引用
        for i in range(len(image_urls)):
            image_filename = f"image_{i+1:02d}"
            lines.append(f"![图片{i+1}](./downloads/{image_filename}.jpg)")
            lines.append(f"*图{i+1}: {image_urls[i]}*")
            lines.append("")
        
        # 原始图片链接
        lines.append("### 原始图片链接")
        for i, url in enumerate(image_urls, 1):
            lines.append(f"{i}. {url}")
    
    return '\n'.join(lines)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='小红书内容获取工具')
    parser.add_argument('url', help='小红书链接')
    parser.add_argument('--account', '-a', default='AI知识账号', 
                       help='账号名称，默认为AI知识账号')
    parser.add_argument('--output', '-o', help='输出目录路径')
    parser.add_argument('--no-download', action='store_true',
                       help='不下载图片，仅提取内容')
    
    args = parser.parse_args()
    
    print("=== 小红书内容获取工具 ===")
    print(f"目标链接: {args.url}")
    print(f"账号名称: {args.account}")
    print(f"下载图片: {'否' if args.no_download else '是'}")
    print("=" * 40)
    
    # 提取内容
    content_data = extract_xhs_content(args.url)
    
    if "error" in content_data:
        print(f"❌ 提取失败: {content_data['error']}")
        return 1
    
    # 显示提取结果
    print("\n✅ 内容提取成功!")
    print(f"标题: {content_data.get('title', '未知')}")
    print(f"作者: {content_data.get('author', '未知')}")
    print(f"笔记ID: {content_data.get('note_id', '未知')}")
    print(f"内容长度: {len(content_data.get('content', ''))} 字符")
    print(f"图片数量: {len(content_data.get('image_urls', []))}")
    print(f"标签数量: {len(content_data.get('tags', []))}")
    
    # 保存内容
    save_dir = save_xhs_content(content_data, args.account, not args.no_download)
    
    if save_dir:
        print(f"\n🎉 内容已保存到: {save_dir}")
        print("\n📁 生成的文件:")
        print(f"  - post_info.json (帖子信息)")
        print(f"  - raw_content.json (原始数据)")
        print(f"  - content.md (Markdown格式)")
        
        # 如果下载了图片，显示图片信息
        if not args.no_download and content_data.get('image_urls'):
            downloads_dir = save_dir / "downloads"
            if downloads_dir.exists():
                image_files = list(downloads_dir.glob("*"))
                if image_files:
                    print(f"  - downloads/ (图片目录，包含 {len(image_files)} 张图片)")
        
        # 显示内容预览
        content = content_data.get('content', '')
        if content:
            preview = content[:200] + "..." if len(content) > 200 else content
            print(f"\n📝 内容预览: {preview}")
    
    return 0

if __name__ == "__main__":
    exit(main())