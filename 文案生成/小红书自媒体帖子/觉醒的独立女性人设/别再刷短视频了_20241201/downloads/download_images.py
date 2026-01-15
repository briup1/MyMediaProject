#!/usr/bin/env python3
"""
下载小红书作品图片
"""

import requests
import os
from pathlib import Path
import time

def download_file(url: str, filepath: Path, timeout: int = 30) -> bool:
    """下载单个文件"""
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()
        
        # 确保目录存在
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ 成功下载: {filepath.name}")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败 {url}: {str(e)}")
        return False

def download_multiple_files(urls: list, output_dir: Path, filename_template: str = "xhs_image_{:02d}") -> dict:
    """批量下载多个文件"""
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
        if '?' in url:
            base_url = url.split('?')[0]
        else:
            base_url = url
        
        if '.' in base_url:
            ext = base_url.split('.')[-1]
            if len(ext) > 5:
                ext = 'png'  # 默认使用png
        else:
            ext = 'png'
        
        filename = f"{filename_template.format(i+1)}.{ext}"
        filepath = output_dir / filename
        
        if download_file(url, filepath):
            results["success"] += 1
        else:
            results["failed"] += 1
            results["failed_urls"].append(url)
        
        # 添加延迟避免请求过快
        time.sleep(1)
    
    print(f"\n📊 批量下载完成:")
    print(f"   成功: {results['success']}/{results['total']}")
    print(f"   失败: {results['failed']}/{results['total']}")
    
    return results

def main():
    """主函数"""
    # 图片URL列表
    image_urls = [
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg004986fpfr5ou9v0egieg?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg0g4986fpfr5ou9qaeu51o?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg104986fpfr5ou9hhbdiho?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg1g4986fpfr5ou9fcdi4g0?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg204986fpfr5ou9tk1qsuo?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg2g4986fpfr5ou91o36v98?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg304986fpfr5ou9i3qm1sg?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg3g4986fpfr5ou9q5l0fh0?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg404986fpfr5ou9cqm6utg?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg4g4986fpfr5ou90gimfio?imageView2/format/png",
        "https://ci.xiaohongshu.com/1040g008311cehtgfmg504986fpfr5ou9g40hab8?imageView2/format/png"
    ]
    
    # 输出目录
    output_dir = Path(__file__).parent
    
    print("=== 小红书图片下载 ===")
    print(f"目标URL数量: {len(image_urls)}")
    print(f"输出目录: {output_dir}")
    print("=" * 40)
    
    # 下载图片
    results = download_multiple_files(image_urls, output_dir, "xhs_image_{:02d}")
    
    if results['success'] > 0:
        print(f"\n✅ 成功下载 {results['success']} 张图片！")
    else:
        print("\n❌ 未能下载任何图片")
    
    return results

if __name__ == "__main__":
    main()