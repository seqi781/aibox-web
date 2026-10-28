#!/usr/bin/env bash
set -euo pipefail
# Retired: the selected architecture serves /aibox/ independently through Nginx.
echo '此同步工具已停用，不能写入主站 public/。请使用 tools/package.py 和 tools/install_release.py 独立发布 aibox；见 docs/DEPLOYMENT.md。' >&2
exit 2
