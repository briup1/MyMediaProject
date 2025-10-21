#!/usr/bin/env python3
"""
下载微信公众号文章中的图片到指定目录
"""

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re

def download_wechat_images(url, output_dir='docs'):
    """
    下载微信公众号文章中的图片
    
    Args:
        url: 微信公众号文章URL
        output_dir: 输出目录，默认为docs
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 获取文章页面
        print(f'正在获取文章页面: {url}')
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找所有图片
        images = soup.find_all('img')
        print(f'找到 {len(images)} 张图片')
        
        downloaded_count = 0
        
        # 下载图片
        for i, img in enumerate(images):
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                # 处理相对路径
                img_url = urljoin(url, img_url)
                
                # 获取图片扩展名
                parsed_url = urlparse(img_url)
                ext = os.path.splitext(parsed_url.path)[1]
                if not ext or len(ext) > 5:  # 如果扩展名不存在或过长，默认为.jpg
                    ext = '.jpg'
                
                # 生成文件名
                filename = f'wechat_article_image_{i+1}{ext}'
                filepath = os.path.join(output_dir, filename)
                
                try:
                    # 下载图片
                    img_response = requests.get(img_url, headers=headers, timeout=30)
                    img_response.raise_for_status()
                    
                    # 保存图片
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    file_size = len(img_response.content)
                    print(f'已下载: {filename} ({file_size} bytes)')
                    downloaded_count += 1
                    
                except Exception as e:
                    print(f'下载失败 {filename}: {e}')
        
        print(f'\n下载完成！成功下载 {downloaded_count} 张图片到 {output_dir} 目录')
        
        # 列出下载的图片文件
        image_files = [f for f in os.listdir(output_dir) if f.startswith('wechat_article_image_')]
        if image_files:
            print('\n下载的图片文件:')
            for img_file in sorted(image_files):
                print(f'  - {img_file}')
        
        return downloaded_count
        
    except requests.RequestException as e:
        print(f'获取页面失败: {e}')
        return 0
    except Exception as e:
        print(f'发生错误: {e}')
        return 0

if __name__ == '__main__':
    # 微信公众号文章URL
    wechat_url = 'https://mp.weixin.qq.com/s/WGFR_Rk037Wlk8cJmWI-vw'
    
    print('=== 微信公众号图片下载工具 ===')
    print(f'目标URL: {wechat_url}')
    print(f'输出目录: docs')
    print('=' * 40)
    
    # 下载图片
    count = download_wechat_images(wechat_url, 'docs')
    
    if count > 0:
        print(f'\n✅ 成功下载 {count} 张图片！')
    else:
        print('\n❌ 未能下载任何图片')