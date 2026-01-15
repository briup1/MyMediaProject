# XHS Content Agent 安装指南

## 插件优化说明 (v0.2.0)

本版本修复了脚本路径和人设路径的解析问题，确保插件在全局安装时能够正常工作。

### 修复的问题

1. **脚本路径解析**：使用 `$CLAUDE_PLUGIN_ROOT` 环境变量动态解析脚本路径
2. **人设路径解析**：使用 `$CLAUDE_PLUGIN_ROOT` 环境变量动态解析人设路径
3. **全局安装支持**：现在支持全局安装到 `~/.claude/plugins/` 目录

## 安装方式

### 方法 1：全局安装（推荐）

```bash
# 复制插件到全局插件目录
cp -r plugins/xhs-content-agent ~/.claude/plugins/

# 验证安装
ls ~/.claude/plugins/xhs-content-agent/
```

### 方法 2：项目本地安装

插件已经在 `plugins/xhs-content-agent/` 目录下，Claude Code 会自动发现。

## 环境变量配置

插件使用 `$CLAUDE_PLUGIN_ROOT` 环境变量来定位资源。该变量由 SessionStart hook 自动设置。

### 全局安装的路径

如果安装到 `~/.claude/plugins/`，hook 会设置：

```bash
CLAUDE_PLUGIN_ROOT=/home/jarvisren/.claude/plugins/xhs-content-agent
```

### 手动设置（如果 hook 不工作）

如果 hook 没有自动设置，可以在调用脚本前手动设置：

```bash
export CLAUDE_PLUGIN_ROOT=/path/to/xhs-content-agent
```

## API 配置

### Qwen-Image API（用于配图生成）

```bash
# 在插件根目录创建 .env 文件
cp plugins/xhs-content-agent/.env.example plugins/xhs-content-agent/.env

# 编辑 .env 文件，添加你的 API Key
nano plugins/xhs-content-agent/.env
```

```env
# 通义千问文生图 API 配置
DASHSCOPE_API_KEY=your-actual-api-key-here

# API 端点（可选，默认使用北京区域）
# DASHSCOPE_API_URL=https://dashscope.aliyuncs.com/api/v1
```

获取 API Key: https://help.aliyun.com/zh/model-studio/get-api-key

## 路径结构

安装后的插件结构：

```
xhs-content-agent/              # $CLAUDE_PLUGIN_ROOT
├── .claude-plugin/
│   └── plugin.json             # 插件清单
├── hooks/
│   └── hooks.json              # SessionStart hook 配置
├── scripts/
│   ├── plugin_paths.py         # 路径解析辅助模块
│   ├── fetch_trending.py       # 热榜获取脚本
│   └── generate_image.py       # 图片生成脚本
├── personas/                   # 人设文件目录
│   ├── 示例人设.md
│   └── 都市独立幼师·生活叙事者人设.md
├── agents/                     # 代理定义
├── commands/                   # 命令定义
├── skills/                     # 技能定义
└── .env                        # API 配置（需创建）
```

## 使用示例

### 测试脚本路径解析

```bash
# 测试路径解析功能
python3 ~/.claude/plugins/xhs-content-agent/scripts/plugin_paths.py
```

### 测试热榜获取

```bash
# 使用环境变量调用脚本
export CLAUDE_PLUGIN_ROOT=/home/jarvisren/.claude/plugins/xhs-content-agent
python3 $CLAUDE_PLUGIN_ROOT/scripts/fetch_trending.py --platform xhs --limit 5
```

### 测试图片生成（需要配置 API Key）

```bash
# 使用环境变量调用脚本
export CLAUDE_PLUGIN_ROOT=/home/jarvisren/.claude/plugins/xhs-content-agent
python3 $CLAUDE_PLUGIN_ROOT/scripts/generate_image.py \
  --prompt "一只可爱的猫咪" \
  --output /tmp/test_cat.jpg
```

## 常见问题

### Q: 脚本找不到？

A: 确保 `$CLAUDE_PLUGIN_ROOT` 环境变量已正确设置：

```bash
echo $CLAUDE_PLUGIN_ROOT
# 应该输出: /home/jarvisren/.claude/plugins/xhs-content-agent
```

### Q: 人设文件找不到？

A: 检查人设目录是否存在：

```bash
ls $CLAUDE_PLUGIN_ROOT/personas/
# 应该看到: 示例人设.md 等文件
```

### Q: Hook 没有自动设置环境变量？

A: 这是当前实现的限制。请在调用命令前手动设置：

```bash
export CLAUDE_PLUGIN_ROOT=/path/to/your/xhs-content-agent
```

### Q: 图片生成失败？

A: 检查以下事项：

1. `.env` 文件是否存在
2. `DASHSCOPE_API_KEY` 是否正确
3. 网络连接是否正常
4. API 余额是否充足

## 开发调试

### 启用调试输出

在命令前添加环境变量：

```bash
CLAUDE_PLUGIN_ROOT=/path/to/plugin CLAUDE_DEBUG=1 /xhs:analyze-trending
```

### 验证 Hook 配置

检查 hook 配置是否正确：

```bash
cat ~/.claude/plugins/xhs-content-agent/hooks/hooks.json
```

### 测试各个组件

```bash
# 测试路径解析
python3 scripts/plugin_paths.py

# 测试热榜获取
python3 scripts/fetch_trending.py --platform xhs --limit 3

# 测试图片生成（需要 API Key）
python3 scripts/generate_image.py --prompt "测试" --output /tmp/test.jpg
```

## 更新日志

### v0.2.0 (2025-01-15)

**修复**：
- 修复脚本路径解析问题
- 修复人设路径解析问题
- 添加 `$CLAUDE_PLUGIN_ROOT` 环境变量支持
- 添加 SessionStart hook 初始化
- 添加路径解析辅助模块 `plugin_paths.py`

**改进**：
- 更新所有 agent 文件使用正确的路径
- 更新所有 command 文件使用正确的路径
- 改进文档说明

### v0.1.0 (2025-01-14)

- 初始版本发布
