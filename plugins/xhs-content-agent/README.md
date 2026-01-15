# 小红书内容开发插件 (XHS Content Agent)

一个专为小红书内容创作者设计的 Claude Code 插件，提供从选题研究到内容发布的完整工作流程。

## 功能特性

### 1. 选题研究
- 分析热榜数据，挖掘爆款潜力
- 评估话题与人设的匹配度
- 从URL/图片/文本中提取创作灵感

### 2. 帖子生成
- 基于人设生成专业的小红书帖子
- 支持交互式创作流程
- 自动创建标准化的目录结构

### 3. 内容优化
- 合规性审核和质量评估
- 提供标题、正文、标签优化建议
- 支持交互式或自动优化

### 4. 配图生成
- 集成 Qwen-Image API 生成图片
- 根据帖子主题自动生成提示词
- 支持多种风格选择

### 5. 自动发布
- 通过 xhs_mcp 发布到小红书
- 发布前确认和内容检查
- 发布记录和数据追踪

## 安装

### 方法1：本地安装

将插件放置在项目的 `plugins/` 目录：

```bash
# 插件已在 plugins/xhs-content-agent/ 目录下
# Claude Code 会自动发现
```

### 方法2：全局安装

复制到用户插件目录：

```bash
cp -r xhs-content-agent ~/.claude/plugins/
```

## 快速开始

### 1. 配置环境变量

#### Qwen-Image API（可选，用于配图生成）

```bash
export DASHSCOPE_API_KEY="your-api-key"
```

获取 API Key: https://help.aliyun.com/zh/model-studio/get-api-key

#### xhs_mcp（可选，用于自动发布）

按照 [xiaohongshu-automation](https://github.com/yourusername/xiaohongshu-automation) 的说明配置 MCP 服务。

### 2. 创建人设文件

在 `personas/` 目录创建你的人设文件：

```bash
cp personas/示例人设.md personas/我的人设.md
# 编辑我的人设.md，填写人设信息
```

### 3. 开始创作

```bash
# 创建第一个帖子
/xhs:create-post
```

## 命令列表

### 帖子创作

| 命令 | 功能 |
|------|------|
| `/xhs:create-post` | 交互式创建帖子 |
| `/xhs:analyze-trending` | 分析热榜选题 |
| `/xhs:analyze-url` | 分析URL/图片/文本 |

### 内容优化

| 命令 | 功能 |
|------|------|
| `/xhs:optimize-post` | 审核和优化帖子 |

### 配图生成

| 命令 | 功能 |
|------|------|
| `/xhs:generate-images` | 生成配图 |

### 发布

| 命令 | 功能 |
|------|------|
| `/xhs:publish` | 发布到平台 |

## 使用示例

### 完整创作流程

```bash
# 1. 从热榜选择选题
/xhs:analyze-trending

# 2. 基于选题创建帖子
/xhs:create-post --topic "AI工具提升办公效率"

# 3. 优化内容
/xhs:optimize-post --file "路径/to/content.md"

# 4. 生成配图
/xhs:generate-images --post "路径/to/content.md"

# 5. 发布到平台
/xhs:publish --post "路径/to/content.md"
```

### 从URL创作

```bash
# 1. 分析爆款内容
/xhs:analyze-url --url "https://www.xiaohongshu.com/explore/..."

# 2. 基于分析结果创作
/xhs:create-post --topic "改编后的主题"
```

## 目录结构

```
xhs-content-agent/
├── .claude-plugin/
│   └── plugin.json          # 插件清单
├── commands/                 # 命令
│   ├── create-post.md
│   ├── analyze-trending.md
│   ├── analyze-url.md
│   ├── optimize-post.md
│   ├── generate-images.md
│   └── publish.md
├── agents/                   # 代理
│   ├── topic-researcher.md
│   ├── post-optimizer.md
│   └── image-generator.md
├── skills/                   # 技能
│   ├── xhs-content-creation/
│   │   └── SKILL.md
│   └── topic-research/
│       └── SKILL.md
├── personas/                 # 人设文件
│   └── 礼例人设.md
├── scripts/                  # 工具脚本
│   ├── fetch_trending.py
│   └── generate_image.py
├── hooks/                    # 钩子配置
├── .mcp.json                 # MCP服务配置
└── README.md                 # 本文件
```

## 组件说明

### Skills（技能）

- **xhs-content-creation**：小红书内容创作专业知识
  - 帖子标准结构
  - 爆款内容要素
  - 合规要求

- **topic-research**：选题研究技巧
  - 热榜分析方法
  - 爆款潜力评估
  - 价值挖掘技巧

### Agents（代理）

- **topic-researcher**：选题研究专家
  - 分析热榜数据
  - 评估爆款潜力
  - 匹配人设定位

- **post-optimizer**：帖子优化专家
  - 合规性审核
  - 质量评估
  - 优化建议生成

- **image-generator**：配图生成专家
  - 分析帖子主题
  - 生成图片提示词
  - 调用 Qwen-Image API

## 配置文件

### MCP 服务配置 (`.mcp.json`)

配置 xhs_mcp 服务用于自动发布：

```json
{
  "mcpServers": {
    "xiaohongshu-automation": {
      "command": "uvx",
      "args": ["--from", "xiaohongshu-automation", "xhs-mcp"]
    }
  }
}
```

## 人设管理

### 创建人设

1. 复制示例模板：
```bash
cp personas/示例人设.md personas/新人设.md
```

2. 编辑人设文件，填写：
- 基本信息
- 性格特点
- 内容风格
- 目标受众
- 创作规范

3. 使用人设：
```bash
/xhs:create-post --persona "新人设"
```

## 预留接口

以下功能当前为预留接口，可按需实现：

### 1. 热榜数据获取 (`scripts/fetch_trending.py`)

当前返回模拟数据，需要时可实现真实的热榜数据获取逻辑。

### 2. 图片后处理

预留以下功能：
- 尺寸调整
- 水印添加
- 文字叠加
- 质量优化

### 3. 定时发布

MCP 服务支持后可实现定时发布功能。

## 开发者指南

### 添加新命令

1. 在 `commands/` 创建新的 `.md` 文件
2. 按照 YAML frontmatter 格式定义元数据
3. 编写命令说明和执行流程

### 添加新技能

1. 在 `skills/` 创建新目录
2. 创建 `SKILL.md` 文件
3. 按照技能模板编写内容

### 添加新代理

1. 在 `agents/` 创建新的 `.md` 文件
2. 定义代理的触发条件和工作流程
3. 指定所需的工具

## 常见问题

### Q: 热榜数据无法获取？
A: 当前热榜接口为预留功能，请手动提供热榜信息或实现 `fetch_trending.py` 中的真实数据获取逻辑。

### Q: 图片生成失败？
A: 检查 `DASHSCOPE_API_KEY` 环境变量是否正确设置。

### Q: 发布功能不可用？
A: 需要先配置并启动 xhs_mcp 服务。

## 贡献

欢迎提交问题和改进建议！

## 许可

MIT License

## 相关链接

- [Claude Code 插件开发文档](https://github.com/anthropics/claude-code)
- [Qwen-Image API 文档](https://help.aliyun.com/zh/model-studio/qwen-image-api)
- [小红书社区规范](https://www.xiaohongshu.com/protocols)

## 更新日志

### v0.2.0 (2025-01-15)

**修复**：
- 修复脚本路径解析问题，支持全局安装
- 修复人设路径解析问题
- 添加 `$CLAUDE_PLUGIN_ROOT` 环境变量支持
- 添加 SessionStart hook 自动初始化
- 添加 `plugin_paths.py` 路径解析辅助模块

**改进**：
- 更新所有 agent 文件使用 `$CLAUDE_PLUGIN_ROOT`
- 更新所有 command 文件使用 `$CLAUDE_PLUGIN_ROOT`
- 改进文档说明，添加安装指南
- 添加测试脚本验证插件功能

### v0.1.0 (2025-01-14)
- 初始版本发布
- 支持选题研究、帖子生成、内容优化、配图生成、自动发布
- 集成 Qwen-Image API
- 预留热榜数据获取接口
