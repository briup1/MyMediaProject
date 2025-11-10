#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin

def get_wechat_article(url, output_dir="."):
    """
    获取微信公众号文章内容和图片
    
    Args:
        url: 微信公众号文章URL
        output_dir: 输出目录
    
    Returns:
        dict: 包含文章标题、内容和图片路径的字典
    """
    # 设置请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    }
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 获取文章内容
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取文章标题
        title = soup.find('h1', class_='rich_media_title')
        if title:
            title_text = title.get_text(strip=True)
        else:
            title_text = soup.find('title').get_text(strip=True)
        
        print(f"文章标题: {title_text}")
        
        # 获取文章内容
        content_div = soup.find('div', class_='rich_media_content')
        if not content_div:
            # 尝试其他可能的class名称
            content_div = soup.find('div', id='js_content')
        
        if content_div:
            # 提取纯文本内容
            content_text = content_div.get_text(separator='\n', strip=True)
            print(f"文章内容长度: {len(content_text)} 字符")
            
            # 提取图片
            images = content_div.find_all('img')
            image_urls = []
            
            for img in images:
                if 'src' in img.attrs:
                    img_url = img['src']
                    # 处理相对路径
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = urljoin(url, img_url)
                    image_urls.append(img_url)
                # 处理data-src属性
                elif 'data-src' in img.attrs:
                    img_url = img['data-src']
                    if not img_url.startswith(('http://', 'https://')):
                        img_url = urljoin(url, img_url)
                    image_urls.append(img_url)
            
            print(f"发现 {len(image_urls)} 张图片")
            
            # 保存内容到文件
            content_file = os.path.join(output_dir, f"{re.sub(r'[\\/:*?\"<>|]', '_', title_text)}_content.txt")
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(f"标题: {title_text}\n\n")
                f.write(content_text)
            print(f"文章内容已保存到: {content_file}")
            
            # 保存图片URL到文件
            if image_urls:
                image_url_file = os.path.join(output_dir, f"{re.sub(r'[\\/:*?\"<>|]', '_', title_text)}_images.txt")
                with open(image_url_file, 'w', encoding='utf-8') as f:
                    for i, img_url in enumerate(image_urls, 1):
                        f.write(f"图片 {i}: {img_url}\n")
                print(f"图片URL已保存到: {image_url_file}")
                
            return {
                "title": title_text,
                "content": content_text,
                "image_urls": image_urls,
                "content_file": content_file,
                "image_url_file": image_url_file if image_urls else None
            }
        else:
            print("未找到文章内容")
            return None
            
    except Exception as e:
        print(f"获取文章失败: {e}")
        return None

if __name__ == "__main__":
    article_url = "https://mp.weixin.qq.com/s/WGFR_Rk037Wlk8cJmWI-vw"
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "output")
    
    result = get_wechat_article(article_url, output_dir)
    if result:
        print("\n获取文章成功!")
    else:
        print("\n获取文章失败")