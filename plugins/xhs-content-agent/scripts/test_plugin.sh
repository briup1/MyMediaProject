#!/bin/bash
# XHS Content Agent 插件测试脚本
# 验证插件功能是否正常工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果统计
PASSED=0
FAILED=0

# 打印测试结果
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $2${NC}"
        ((FAILED++))
    fi
}

# 检查环境变量
check_env() {
    echo -e "\n${YELLOW}=== 检查环境变量 ===${NC}"

    if [ -z "$CLAUDE_PLUGIN_ROOT" ]; then
        echo -e "${YELLOW}⚠ CLAUDE_PLUGIN_ROOT 未设置，使用当前目录推断${NC}"
        export CLAUDE_PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    fi

    echo "CLAUDE_PLUGIN_ROOT: $CLAUDE_PLUGIN_ROOT"

    # 检查目录结构
    [ -d "$CLAUDE_PLUGIN_ROOT" ]
    print_result $? "插件根目录存在"

    [ -d "$CLAUDE_PLUGIN_ROOT/scripts" ]
    print_result $? "scripts 目录存在"

    [ -d "$CLAUDE_PLUGIN_ROOT/personas" ]
    print_result $? "personas 目录存在"

    [ -d "$CLAUDE_PLUGIN_ROOT/agents" ]
    print_result $? "agents 目录存在"

    [ -d "$CLAUDE_PLUGIN_ROOT/commands" ]
    print_result $? "commands 目录存在"

    [ -f "$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json" ]
    print_result $? "plugin.json 存在"

    [ -f "$CLAUDE_PLUGIN_ROOT/hooks/hooks.json" ]
    print_result $? "hooks.json 存在"
}

# 测试路径解析
test_path_resolution() {
    echo -e "\n${YELLOW}=== 测试路径解析 ===${NC}"

    python3 -c "
import sys
sys.path.insert(0, '$CLAUDE_PLUGIN_ROOT/scripts')
from plugin_paths import get_plugin_root, get_script_path, get_persona_path

root = get_plugin_root()
print(f'插件根目录: {root}')
assert root.exists(), '插件根目录不存在'

script = get_script_path('fetch_trending.py')
print(f'脚本路径: {script}')
assert script.exists(), '脚本文件不存在'

persona = get_persona_path('示例人设.md')
print(f'人设路径: {persona}')
assert persona.exists(), '人设文件不存在'

print('✓ 路径解析测试通过')
" && print_result 0 "路径解析模块" || print_result 1 "路径解析模块"
}

# 测试热榜获取脚本
test_fetch_trending() {
    echo -e "\n${YELLOW}=== 测试热榜获取脚本 ===${NC}"

    python3 "$CLAUDE_PLUGIN_ROOT/scripts/fetch_trending.py" --platform xhs --limit 3 > /tmp/trending_test.json 2>&1
    print_result $? "fetch_trending.py 执行"

    # 检查输出
    if [ -f /tmp/trending_test.json ]; then
        python3 -c "
import json
with open('/tmp/trending_test.json') as f:
    data = json.load(f)
assert data['platform'] == 'xhs', '平台不正确'
assert data['count'] > 0, '没有获取到数据'
assert 'data' in data, '缺少 data 字段'
print('✓ 数据格式验证通过')
" && print_result 0 "热榜数据格式" || print_result 1 "热榜数据格式"
    fi
}

# 测试图片生成脚本（无 API Key 时跳过）
test_generate_image() {
    echo -e "\n${YELLOW}=== 测试图片生成脚本 ===${NC}"

    # 检查是否有 API Key
    if [ ! -f "$CLAUDE_PLUGIN_ROOT/.env" ] || ! grep -q "DASHSCOPE_API_KEY=" "$CLAUDE_PLUGIN_ROOT/.env"; then
        echo -e "${YELLOW}⚠ 未配置 DASHSCOPE_API_KEY，跳过图片生成测试${NC}"
        echo "  要测试图片生成，请在 .env 文件中配置 API Key"
        return
    fi

    echo -e "${YELLOW}检测到 API Key，测试图片生成...${NC}"

    # 这里只测试脚本是否能启动，不实际生成图片
    python3 "$CLAUDE_PLUGIN_ROOT/scripts/generate_image.py" --help > /dev/null 2>&1
    print_result $? "generate_image.py 帮助信息"

    echo -e "${YELLOW}注意：完整测试需要有效的 API Key${NC}"
}

# 测试人设文件
test_personas() {
    echo -e "\n${YELLOW}=== 测试人设文件 ===${NC}"

    [ -f "$CLAUDE_PLUGIN_ROOT/personas/示例人设.md" ]
    print_result $? "示例人设.md 存在"

    # 检查人设文件内容
    if [ -f "$CLAUDE_PLUGIN_ROOT/personas/示例人设.md" ]; then
        grep -q "##" "$CLAUDE_PLUGIN_ROOT/personas/示例人设.md"
        print_result $? "示例人设.md 格式正确"
    fi
}

# 测试代理文件
test_agents() {
    echo -e "\n${YELLOW}=== 测试代理文件 ===${NC}"

    for agent in topic-researcher post-optimizer image-generator; do
        [ -f "$CLAUDE_PLUGIN_ROOT/agents/$agent.md" ]
        print_result $? "agents/$agent.md 存在"

        # 检查是否使用了正确的路径
        if [ -f "$CLAUDE_PLUGIN_ROOT/agents/$agent.md" ]; then
            grep -q "CLAUDE_PLUGIN_ROOT" "$CLAUDE_PLUGIN_ROOT/agents/$agent.md" || \
            [ "$agent" == "post-optimizer" ]  # post-optimizer 可能不需要
            print_result $? "agents/$agent.md 使用正确的路径引用"
        fi
    done
}

# 测试命令文件
test_commands() {
    echo -e "\n${YELLOW}=== 测试命令文件 ===${NC}"

    for cmd in create-post analyze-trending analyze-url generate-images optimize-post publish; do
        [ -f "$CLAUDE_PLUGIN_ROOT/commands/$cmd.md" ]
        print_result $? "commands/$cmd.md 存在"
    done
}

# 测试 hooks 配置
test_hooks() {
    echo -e "\n${YELLOW}=== 测试 Hooks 配置 ===${NC}"

    python3 -c "
import json
with open('$CLAUDE_PLUGIN_ROOT/hooks/hooks.json') as f:
    hooks = json.load(f)
assert 'SessionStart' in hooks, '缺少 SessionStart hook'
assert len(hooks['SessionStart']) > 0, 'SessionStart hook 为空'
print('✓ Hooks 配置格式正确')
" && print_result 0 "hooks.json 格式" || print_result 1 "hooks.json 格式"
}

# 测试 plugin.json
test_plugin_json() {
    echo -e "\n${YELLOW}=== 测试 plugin.json ===${NC}"

    python3 -c "
import json
with open('$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json') as f:
    config = json.load(f)
assert config['name'] == 'xhs-content-agent', '插件名称不正确'
assert config['version'] == '0.2.0', '版本号应该是 0.2.0'
assert 'hooks' in config, '缺少 hooks 配置'
print('✓ plugin.json 配置正确')
" && print_result 0 "plugin.json 配置" || print_result 1 "plugin.json 配置"
}

# 主测试流程
main() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  XHS Content Agent 插件测试${NC}"
    echo -e "${GREEN}========================================${NC}"

    check_env
    test_path_resolution
    test_fetch_trending
    test_generate_image
    test_personas
    test_agents
    test_commands
    test_hooks
    test_plugin_json

    # 输出测试结果
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  测试结果汇总${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "通过: ${GREEN}$PASSED${NC}"
    echo -e "失败: ${RED}$FAILED${NC}"
    echo -e "总计: $((PASSED + FAILED))"

    if [ $FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✓ 所有测试通过！${NC}"
        exit 0
    else
        echo -e "\n${RED}✗ 部分测试失败${NC}"
        exit 1
    fi
}

# 运行测试
main
