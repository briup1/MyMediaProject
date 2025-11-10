#!/usr/bin/env python3
"""
下载小红书作品中的图片到项目中
使用新的模块化架构
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.content_manager import ContentManager, create_xhs_post
from src.utils.download_images_from_urls import download_multiple_files

def download_xhs_images(post_id: str = "68f655e80000000005038817", 
                       title: str = "DeepSeek-OCR让我看到了AI的另一种可能",
                       image_urls: list = None,
                       account_name: str = "AI知识账号"):
    """
    下载小红书图片
    
    Args:
        post_id: 小红书作品ID
        title: 作品标题
        image_urls: 图片URL列表
        account_name: 账号名称
    """
    # 默认图片URL列表（示例）
    if image_urls is None:
        image_urls = [
            # 在这里添加实际的图片URLs
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ]
    
    # 创建内容管理器
    manager = ContentManager()
    
    # 创建帖子目录
    post_dir = manager.create_post_directory(post_id, title, account_name)
    print(f"创建目录: {post_dir}")
    
    # 准备帖子信息
    post_info = {
        "title": title,
        "post_id": post_id,
        "url": f"https://www.xiaohongshu.com/explore/{post_id}",
        "author": "爱学习的乔同学",
        "publish_time": "2025-10-20_15:31:53",
        "tags": "#人工智能 #大模型 #DeepSeek #OCR #物理神经网络",
        "description": """这篇文章非常干

DeepSeek-OCR出了之后，反响平平，也似乎没有人注意到它的思想，也就是利用连续超越离散，用二维的信息密度超越一维。

那么，我们还能不能继续探索呢？

有不同的见解，欢迎一起交流。"""
    }
    
    # 保存帖子信息
    info_path = manager.save_post_info(post_dir, post_info)
    print(f"保存帖子信息到: {info_path}")
    
    # 下载图片到downloads目录
    downloads_dir = post_dir / "downloads"
    results = download_multiple_files(image_urls, downloads_dir, "image_{:02d}")
    
    print(f"\n下载完成! 成功下载 {results['success']}/{results['total']} 张图片到目录: {downloads_dir}")
    
    # 如果有失败的下载，显示失败的URL
    if results['failed_urls']:
        print("\n❌ 下载失败的URL:")
        for url in results['failed_urls']:
            print(f"  - {url}")
    
    return post_dir, results

def main():
    """主函数"""
    # 示例使用
    post_id = "68f655e80000000005038817"
    title = "DeepSeek-OCR让我看到了AI的另一种可能"
    
    # 注意：请替换为实际的图片URLs
    image_urls = [
        # "https://example.com/image1.jpg",
        # "https://example.com/image2.jpg"
    ]
    
    print("=== 小红书图片下载工具 ===")
    print(f"作品ID: {post_id}")
    print(f"作品标题: {title}")
    print("=" * 40)
    
    # 如果提供了图片URL，则下载图片
    if image_urls:
        post_dir, results = download_xhs_images(post_id, title, image_urls)
        if results['success'] > 0:
            print(f"\n✅ 成功下载 {results['success']} 张图片！")
        else:
            print("\n❌ 未能下载任何图片")
    else:
        # 仅创建目录结构和信息文件
        manager = ContentManager()
        post_dir = manager.create_post_directory(post_id, title)
        post_info = {
            "title": title,
            "post_id": post_id,
            "url": f"https://www.xiaohongshu.com/explore/{post_id}",
            "author": "爱学习的乔同学",
            "publish_time": "2025-10-20_15:31:53",
            "tags": "#人工智能 #大模型 #DeepSeek #OCR #物理神经网络",
            "description": """这篇文章非常干

DeepSeek-OCR出了之后，反响平平，也似乎没有人注意到它的思想，也就是利用连续超越离散，用二维的信息密度超越一维。

那么，我们还能不能继续探索呢？

有不同的见解，欢迎一起交流。"""
        }
        info_path = manager.save_post_info(post_dir, post_info)
        print(f"创建目录结构完成: {post_dir}")
        print(f"保存帖子信息到: {info_path}")
        print("\n💡 请在代码中添加实际的图片URLs以下载图片")

if __name__ == "__main__":
    main()