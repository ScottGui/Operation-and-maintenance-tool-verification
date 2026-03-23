#!/bin/bash

# ============================================
# 一键同步至 Git 脚本
# 功能：自动提交本地更改、推送到远程仓库，并生成同步日志
# 用法：./sync-to-git.sh [提交信息]
# ============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志文件路径
SYNC_LOG="docs/git-sync-log.md"

# 获取当前时间
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
CURRENT_DATE=$(date "+%Y-%m-%d")

# 获取提交信息
if [ -z "$1" ]; then
    COMMIT_MESSAGE="更新于 ${CURRENT_TIME}"
else
    COMMIT_MESSAGE="$1"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  开始同步至 Git 仓库${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查是否在 git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}错误：当前目录不是 Git 仓库${NC}"
    exit 1
fi

# 获取仓库信息
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
BRANCH_NAME=$(git branch --show-current)
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "未设置")

echo -e "${YELLOW}仓库信息：${NC}"
echo "  仓库名称: $REPO_NAME"
echo "  当前分支: $BRANCH_NAME"
echo "  远程地址: $REMOTE_URL"
echo ""

# 步骤 1: 获取同步前的状态
echo -e "${BLUE}[1/5] 获取同步前状态...${NC}"
BEFORE_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "none")
BEFORE_COMMIT_SHORT=$(echo $BEFORE_COMMIT | cut -c1-7)

# 获取远程最新状态
git fetch origin $BRANCH_NAME 2>/dev/null || true

echo "  本地提交: $BEFORE_COMMIT_SHORT"
echo ""

# 步骤 2: 检查是否有更改
echo -e "${BLUE}[2/5] 检查本地更改...${NC}"
if git diff-index --quiet HEAD -- && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo -e "${YELLOW}  没有检测到本地更改${NC}"
    
    # 检查是否需要拉取远程更新
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")
    
    if [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
        echo -e "${YELLOW}  但远程仓库有更新，执行拉取...${NC}"
        git pull origin $BRANCH_NAME
        echo -e "${GREEN}  已同步远程更新${NC}"
    else
        echo -e "${GREEN}  本地与远程已同步，无需操作${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  同步完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
    exit 0
fi

# 显示更改摘要
echo -e "${YELLOW}  检测到以下更改：${NC}"
git status --short | head -20
if [ $(git status --short | wc -l) -gt 20 ]; then
    echo "  ... 还有 $(($(git status --short | wc -l) - 20)) 个文件"
fi
echo ""

# 步骤 3: 添加更改
echo -e "${BLUE}[3/5] 添加更改到暂存区...${NC}"
git add .
echo -e "${GREEN}  已添加所有更改${NC}"
echo ""

# 步骤 4: 提交更改
echo -e "${BLUE}[4/5] 提交更改...${NC}"
git commit -m "$COMMIT_MESSAGE"
if [ $? -ne 0 ]; then
    echo -e "${RED}  提交失败${NC}"
    exit 1
fi
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_HASH_SHORT=$(echo $COMMIT_HASH | cut -c1-7)
echo -e "${GREEN}  提交成功: $COMMIT_HASH_SHORT${NC}"
echo ""

# 步骤 5: 推送到远程
echo -e "${BLUE}[5/5] 推送到远程仓库...${NC}"
git push origin $BRANCH_NAME
if [ $? -ne 0 ]; then
    echo -e "${RED}  推送失败${NC}"
    exit 1
fi
echo -e "${GREEN}  推送成功${NC}"
echo ""

# ============================================
# 生成同步日志
# ============================================
echo -e "${BLUE}生成同步日志...${NC}"

# 创建日志目录
mkdir -p docs

# 获取更改统计
FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r $COMMIT_HASH | wc -l | tr -d ' ')
INSERTIONS=$(git diff --shortstat $BEFORE_COMMIT $COMMIT_HASH | grep -o '[0-9]* insertion' | grep -o '[0-9]*' || echo "0")
DELETIONS=$(git diff --shortstat $BEFORE_COMMIT $COMMIT_HASH | grep -o '[0-9]* deletion' | grep -o '[0-9]*' || echo "0")

# 获取更改的文件列表
CHANGED_FILES_LIST=$(git diff-tree --no-commit-id --name-only -r $COMMIT_HASH | head -10)

# 生成日志内容
LOG_ENTRY="## ${CURRENT_DATE} ${CURRENT_TIME}

### 同步摘要
- **提交哈希**: \`$COMMIT_HASH_SHORT\`
- **提交信息**: $COMMIT_MESSAGE
- **分支**: \`$BRANCH_NAME\`
- **作者**: $(git config user.name) <$(git config user.email)>

### 更改统计
- **修改文件数**: $FILES_CHANGED 个
- **新增行数**: ${INSERTIONS:-0} 行
- **删除行数**: ${DELETIONS:-0} 行

### 主要变更文件
\`\`\`
$CHANGED_FILES_LIST
\`\`\`

### 详细变更
\`\`\`
$(git diff --stat $BEFORE_COMMIT $COMMIT_HASH 2>/dev/null || echo '首次提交')
\`\`\`

---

"

# 如果日志文件不存在，创建头部
if [ ! -f "$SYNC_LOG" ]; then
    echo "# Git 同步日志

> 本文件由 sync-to-git.sh 自动生成，记录每次同步的详细信息

" > "$SYNC_LOG"
fi

# 将新日志插入到文件头部（保持倒序）
TEMP_FILE=$(mktemp)
echo "$LOG_ENTRY" > "$TEMP_FILE"
cat "$SYNC_LOG" >> "$TEMP_FILE"
mv "$TEMP_FILE" "$SYNC_LOG"

echo -e "${GREEN}  日志已写入: $SYNC_LOG${NC}"
echo ""

# ============================================
# 完成
# ============================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  同步完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}同步摘要：${NC}"
echo "  提交: $COMMIT_HASH_SHORT"
echo "  信息: $COMMIT_MESSAGE"
echo "  文件: $FILES_CHANGED 个"
echo "  分支: $BRANCH_NAME"
echo ""
echo -e "${BLUE}查看日志: ${NC}cat $SYNC_LOG"
