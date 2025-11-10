"""
下载工具模块
提供通用的下载功能
"""

import os
import requests
from pathlib import Path
from typing import Optional
from config.settings import DOWNLOAD_CONFIG


def download_file(url: str, filepath: Path, timeout: Optional[int] = None) -> bool:
    """
    下载文件到指定路径
    
    Args:
        url: 文件URL
        filepath: 保存路径
        timeout: 超时时间（秒）
    
    Returns:
        bool: 下载是否成功
    """
    if timeout is None:
        timeout = DOWNLOAD_CONFIG["timeout"]
    
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()
        
        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ 成功下载文件: {filepath.name}")
        return True
        
    except Exception as e:
        print(f"❌ 下载文件失败 {url}: {str(e)}")
        return False


def download_file_with_retry(url: str, filepath: Path, max_retries: Optional[int] = None) -> bool:
    """
    带重试机制的文件下载
    
    Args:
        url: 文件URL
        filepath: 保存路径
        max_retries: 最大重试次数
    
    Returns:
        bool: 下载是否成功
    """
    if max_retries is None:
        max_retries = DOWNLOAD_CONFIG["retry_attempts"]
    
    for attempt in range(max_retries + 1):
        if download_file(url, filepath):
            return True
        
        if attempt < max_retries:
            print(f"⚠️ 第{attempt + 1}次下载失败，{DOWNLOAD_CONFIG['timeout']}秒后重试...")
            import time
            time.sleep(DOWNLOAD_CONFIG['timeout'])
    
    return False


def download_multiple_files(urls: list, output_dir: Path, filename_template: str = "file_{:03d}") -> dict:
    """
    批量下载多个文件
    
    Args:
        urls: 文件URL列表
        output_dir: 输出目录
        filename_template: 文件名模板
    
    Returns:
        dict: 下载结果统计
    """
    results = {
        "total": len(urls),
        "success": 0,
        "failed": 0,
        "failed_urls": []
    }
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i, url in enumerate(urls):
        # 从URL推断文件扩展名
        parsed_url = requests.utils.urlparse(url)
        path = parsed_url.path
        
        # 获取文件扩展名
        if '.' in path:
            ext = path.split('.')[-1]
            # 限制扩展名长度
            if len(ext) > 5:
                ext = 'bin'
        else:
            ext = 'bin'
        
        filename = f"{filename_template.format(i+1)}.{ext}"
        filepath = output_dir / filename
        
        if download_file_with_retry(url, filepath):
            results["success"] += 1
        else:
            results["failed"] += 1
            results["failed_urls"].append(url)
    
    print(f"\n📊 批量下载完成:")
    print(f"   成功: {results['success']}/{results['total']}")
    print(f"   失败: {results['failed']}/{results['total']}")
    
    return results


def get_file_extension_from_url(url: str) -> str:
    """
    从URL获取文件扩展名
    
    Args:
        url: 文件URL
    
    Returns:
        str: 文件扩展名
    """
    parsed_url = requests.utils.urlparse(url)
    path = parsed_url.path
    
    if '.' in path:
        ext = path.split('.')[-1].lower()
        # 常见图片格式
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        if ext in image_extensions:
            return ext
        elif ext == 'jpeg':
            return 'jpg'
        else:
            return 'bin'
    else:
        return 'bin'


if __name__ == "__main__":
    # 测试下载功能
    test_urls = [
        "替换为实际的图片URLs"
    ]
    
    test_dir = Path("/tmp/test_download")
    results = download_multiple_files(test_urls, test_dir)
    print("测试结果:", results)