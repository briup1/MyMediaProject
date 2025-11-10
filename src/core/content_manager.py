"""
内容管理器
负责管理小红书等内容的目录结构和元数据
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List


class ContentManager:
    """内容管理器类"""
    
    def __init__(self, base_path: str = "文案生成/小红书自媒体帖子"):
        """
        初始化内容管理器
        
        Args:
            base_path: 基础路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def create_post_directory(self, post_id: str, title: str, account_name: str = "AI知识账号") -> Path:
        """
        为小红书帖子创建目录
        
        Args:
            post_id: 帖子ID
            title: 帖子标题
            account_name: 账号名称
            
        Returns:
            Path: 创建的目录路径
        """
        # 清理标题中的非法字符
        clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        # 添加时间戳确保唯一性
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = f"{clean_title}_{timestamp}"
        
        # 构建完整路径
        post_dir = self.base_path / account_name / dir_name
        
        # 创建目录结构
        post_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (post_dir / "downloads").mkdir(exist_ok=True)
        (post_dir / "research").mkdir(exist_ok=True)
        (post_dir / "drafts").mkdir(exist_ok=True)
        (post_dir / "final").mkdir(exist_ok=True)
        
        return post_dir
    
    def save_post_info(self, post_dir: Path, post_info: dict) -> Path:
        """
        保存帖子信息到Markdown文件
        
        Args:
            post_dir: 帖子目录路径
            post_info: 帖子信息字典
            
        Returns:
            Path: 保存的文件路径
        """
        info_content = f"""# 小红书帖子信息

- **作品标题**: {post_info.get('title', '')}
- **作品ID**: {post_info.get('post_id', '')}
- **作品链接**: {post_info.get('url', '')}
- **作者昵称**: {post_info.get('author', '')}
- **发布时间**: {post_info.get('publish_time', '')}
- **标签**: {post_info.get('tags', '')}

## 内容描述

{post_info.get('description', '')}
"""
        
        info_path = post_dir / "帖子信息.md"
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(info_content)
        
        return info_path


def create_xhs_post(post_id: str, title: str, account_name: str = "AI知识账号") -> Path:
    """
    创建小红书帖子目录的便捷函数
    
    Args:
        post_id: 帖子ID
        title: 帖子标题
        account_name: 账号名称
        
    Returns:
        Path: 创建的目录路径
    """
    manager = ContentManager()
    return manager.create_post_directory(post_id, title, account_name)