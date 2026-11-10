#!/usr/bin/env bash
# 一键把 deal-hunter 推到 GitHub 并开启 Pages。
# 前置：gh auth login 已完成（box 上已登录 wenjianmin24-pixel）。
set -euo pipefail
cd "$(dirname "$0")"

REPO_NAME="${1:-deal-hunter}"
OWNER=$(gh api user --jq .login)
echo "==> owner: $OWNER  repo: $REPO_NAME"

# hunter.db 要进仓库：它是数据本身（含 first_seen，丢了就丢历史）
cat > .gitignore <<'EOF'
__pycache__/
*.pyc
site/data.js
verify.log
collect.log
EOF

if [ ! -d .git ]; then git init -q; fi
git config user.name  "deal-hunter-bot"
git config user.email "bot@users.noreply.github.com"
git checkout -q -B main 2>/dev/null || git branch -M main

git add -A
git commit -q -m "global deal hunter: collectors, classifier, static dashboard" || echo "nothing to commit"

if gh repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1; then
  echo "==> repo exists, pushing"
  git remote remove origin >/dev/null 2>&1 || true
  git remote add origin "https://github.com/$OWNER/$REPO_NAME.git"
  git push -u origin main --force
else
  echo "==> creating repo"
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push \
     --description "GLOBAL DEAL HUNTER · 全球羊毛情报中心（自动采集 + 核链 + 静态看板）"
fi

echo "==> enabling Pages"
gh api -X POST "/repos/$OWNER/$REPO_NAME/pages" -f build_type=workflow >/dev/null 2>&1 \
  || gh api -X PUT "/repos/$OWNER/$REPO_NAME/pages" -f build_type=workflow >/dev/null 2>&1 \
  || echo "   (Pages 可能已启用)"

echo "==> triggering workflow"
gh workflow run hunt.yml -R "$OWNER/$REPO_NAME" 2>/dev/null || \
  gh api -X POST "/repos/$OWNER/$REPO_NAME/actions/workflows/hunt.yml/dispatches" \
     -f ref=main >/dev/null

echo
echo "==> 完成"
echo "    仓库 : https://github.com/$OWNER/$REPO_NAME"
echo "    页面 : https://$OWNER.github.io/$REPO_NAME/"
