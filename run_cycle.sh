#!/usr/bin/env bash
# 一轮完整循环：采集 → 核链 → 导出
set -uo pipefail
cd "$(dirname "$0")"
echo "=== $(date -u '+%F %T') UTC collect ==="
python3 collect.py 2>&1 | tail -3
echo "=== verify (60 newest) ==="
timeout 600 python3 verify.py --limit 60 --delay 0.1 2>&1 | tail -5
echo "=== export ==="
python3 export.py site
