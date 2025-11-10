#!/usr/bin/env python3
"""
下载小红书作品中的图片到项目中
使用新的模块化架构
"""

import os
from pathlib import Path
from src.core.content_manager import ContentManager, create_xhs_post
from src.utils.download_images_from_urls import download_multiple_files

def download_xhs_images():
    """下载小红书图片"""
    # 小红书作品信息
    post_id = "68f655e80000000005038817"
    title = "DeepSeek-OCR让我看到了AI的另一种可能"
    
    # 图片下载地址列表
    image_urls = [
        "替换为实际的图片URLs"
    ]
    
    # 创建目录
    post_dir = create_directory_for_post(post_id, title)
    print(f"创建目录: {post_dir}")
    
    # 保存帖子信息
    info_content = f"""# 小红书帖子信息

- **作品标题**: DeepSeek-OCR让我看到了AI的另一种可能
- **作品ID**: {post_id}
- **作品链接**: https://www.xiaohongshu.com/explore/{post_id}
- **作者昵称**: 爱学习的乔同学
- **发布时间**: 2025-10-20_15:31:53
- **标签**: #人工智能 #大模型 #DeepSeek #OCR #物理神经网络

## 内容描述

这篇文章非常干

DeepSeek-OCR出了之后，反响平平，也似乎没有人注意到它的思想，也就是利用连续超越离散，用二维的信息密度超越一维。

那么，我们还能不能继续探索呢？

有不同的见解，欢迎一起交流。
"""
    
    info_path = os.path.join(post_dir, "帖子信息.md")
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(info_content)
    
    print(f"保存帖子信息到: {info_path}")
    
    # 下载图片
    success_count = 0
    for i, url in enumerate(image_urls, 1):
        # 生成文件名
        filename = f"image_{i:02d}.png"
        filepath = os.path.join(post_dir, filename)
        
        # 下载图片
        if download_image(url, filepath):
            success_count += 1
    
    print(f"\n下载完成! 成功下载 {success_count}/{len(image_urls)} 张图片到目录: {post_dir}")
    return post_dir

if __name__ == "__main__":
    download_xhs_images()