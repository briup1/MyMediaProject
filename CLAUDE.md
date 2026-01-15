# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 项目概述

**MyMediaProject** 是一个专为新媒体运营人员设计的实用工作平台。这是一个基于 Python 的平台，专注于**内容创作流程管理**、**角色 prompt 沉淀**和**运营工具集成**。

### 核心理念

- **内容为核**：一切围绕内容生成和管理展开
- **角色驱动**：基于存储在 `docs/roles/` 中的预定义角色/人设生成内容
- **流程导向**：标准操作流程（SOP）指导内容创作
- **工具辅助**：自动化工具服务于运营流程，而非反之

## 开发命令

### 包管理

```bash
# 使用 uv 安装依赖
uv sync

# 运行 Python 脚本
uv run python src/tools/get_xhs_content.py <url>
```

### 常用工具

```bash
# 提取小红书内容
python src/tools/get_xhs_content.py <url> --account <账号名称>

# 下载小红书图片
python src/tools/download_xhs_images.py

# 提取微信公众号文章内容
python src/tools/get_wechat_article.py <url>

# 下载微信公众号图片
python src/tools/download_wechat_images.py
```

### 测试

目前没有正式的测试套件。添加测试时，请将测试文件放在 `tests/` 目录中并使用 pytest。

## 架构设计

### 内容处理流程

```
角色定义 (docs/roles/) → 内容生成 → 素材收集 → 内容组织 → 存储 (文案生成/)
```

### 核心架构组件

1. **内容管理器** ([`src/core/content_manager.py`](src/core/content_manager.py))
   - 负责创建帖子的目录结构
   - 管理元数据存储（Markdown + JSON）
   - 创建标准化的子目录：`downloads/`、`research/`、`drafts/`、`final/`

2. **提取器工具** ([`src/tools/`](src/tools/))
   - 针对特定平台的内容提取器（小红书、微信）
   - 每个工具遵循一致的流程：提取 → 保存 → 下载素材
   - 使用 BeautifulSoup 并配备多个备用选择器以提高稳定性

3. **下载器工具** ([`src/utils/`](src/utils/))
   - 带重试逻辑的通用图片下载功能
   - 可从 [`config/settings.py`](config/settings.py) 配置超时和延迟

4. **角色系统** ([`docs/roles/`](docs/roles/))
   - 包含详细 prompt 模板的角色定义
   - 每个账号/品牌都有自己的角色文件
   - 定义语调、风格、内容要求

5. **SOP 框架** ([`docs/SOP沉淀/`](docs/SOP沉淀/))
   - 内容创作的标准化工作流程
   - 记录经过验证的流程以确保一致性

### 目录结构

```
MyMediaProject/
├── docs/
│   ├── roles/              # 角色定义和 prompt 模板
│   └── SOP沉淀/            # 标准操作流程
├── 文案生成/                # 生成的内容存储（已加入 gitignore）
│   ├── 小红书自媒体帖子/    # 小红书内容
│   └── 微信公众号帖子/      # 微信内容
├── src/
│   ├── core/               # 核心业务逻辑
│   ├── tools/              # 特定平台的提取工具
│   └── utils/              # 通用工具
├── config/                 # 配置文件
└── plugins/                # 额外的代理/角色
```

## 代码规范

### 工具实现模式

创建新的平台提取工具时：

1. 参考 [`get_xhs_content.py`](src/tools/get_xhs_content.py:23-101) 的结构
2. 使用多个选择器备用方案以提高稳定性（参见 [`extract_title()`](src/tools/get_xhs_content.py:125-143)）
3. 返回带有错误处理的结构化字典
4. 集成 `ContentManager` 进行存储
5. 使用 argparse 支持命令行参数

### 内容存储模式

- 使用 `ContentManager.create_post_directory()` 创建标准化的目录结构
- 将元数据同时保存为人类可读的 Markdown 和机器可读的 JSON
- 将素材下载到 `downloads/` 子目录
- 包含时间戳以确保唯一性

### 导入模式

工具应将项目根目录添加到 Python 路径：

```python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.core.content_manager import ContentManager
```

## 配置

配置项管理在 [`config/settings.py`](config/settings.py)：
- `timeout`：请求超时时间（秒）（默认：30）
- `retry_attempts`：重试次数（默认：3）
- `delay_between_requests`：请求间延迟以避免被封禁（默认：1秒）

## 使用角色

添加或修改角色时：

1. 在 [`docs/roles/`](docs/roles/) 中创建/更新文件
2. 包含：角色定义、语调/风格指南、内容模板
3. 生成内容时引用相应的角色
4. 根据效果数据更新角色定义

## 内容组织

生成的内容遵循以下结构：

```
文案生成/<平台>/<账号名称>/<帖子标题>_<时间戳>/
├── downloads/    # 下载的图片/素材
├── research/     # 研究资料
├── drafts/       # 草稿版本
├── final/        # 最终内容
├── 帖子信息.md   # 帖子元数据
├── content.md    # Markdown 格式内容
└── raw_content.json  # 原始提取数据
```

## 重要说明

- `文案生成/` 目录已加入 gitignore（包含用户生成的内容）
- 所有文档使用中文 - 更新文档时请保持语言一致性
- 工具优先考虑稳定性而非速度（多个选择器、重试逻辑）
- 内容同时存储为 Markdown 和 JSON 以便于人类和机器阅读
- 特定平台的反爬虫措施需要正确的请求头和请求节流
