#!/usr/bin/env bash
# 把 aibox 宣传站复制进一个 Next.js 项目，作为独立子页面（默认挂在 /aibox）。
#
# 用法：
#   bash nextjs/sync.sh <Next.js 项目目录> [--base /aibox] [--domain example.com]
#
# 做的事：
#   1. 把页面和资源复制到 <项目>/public<base>/
#   2. 把页面里的相对路径改成以 <base> 开头的绝对路径
#   3. 打印需要加到 next.config 里的 rewrites
# 不会改动 Next.js 项目里的任何其他文件。页面有自己的 CSS 和 JS，不受站点全局样式影响。
set -euo pipefail

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

TARGET="" BASE="/aibox" DOMAIN=""
while [ $# -gt 0 ]; do
  case "$1" in
    --base)   BASE="${2:?--base 需要一个值}"; shift 2 ;;
    --domain) DOMAIN="${2:?--domain 需要一个值}"; shift 2 ;;
    -h|--help) usage 0 ;;
    -*) echo "未知参数：$1" >&2; usage 1 ;;
    *) TARGET="$1"; shift ;;
  esac
done
[ -n "$TARGET" ] || usage 1

# base 规范成 /xxx 形式：有前导斜杠，没有尾斜杠
BASE="/${BASE#/}"; BASE="${BASE%/}"
[ "$BASE" != "/" ] && [ -n "$BASE" ] || { echo "--base 不能是根路径" >&2; exit 1; }

SRC="$(cd "$(dirname "$0")/.." && pwd)"
if ! ls "$TARGET"/next.config.* >/dev/null 2>&1; then
  echo "在 $TARGET 里没找到 next.config.*，这不像一个 Next.js 项目。" >&2
  exit 1
fi
OUT="$TARGET/public$BASE"

rm -rf "$OUT"
mkdir -p "$OUT/assets" "$OUT/en" "$OUT/init"
cp "$SRC/assets/site.css" "$SRC/assets/site.js" "$SRC/assets/cast-player.js" "$OUT/assets/"
[ -f "$SRC/init/cast.js" ] && cp "$SRC/init/cast.js" "$OUT/init/"
cp "$SRC/favicon.svg" "$SRC/og.svg" "$OUT/"
[ -f "$SRC/og.png" ] && cp "$SRC/og.png" "$OUT/"

# 资源版本号：内容变了版本号就变，浏览器不会继续用缓存里的旧 CSS / JS / 录制数据
VER="$(cat "$SRC"/assets/*.css "$SRC"/assets/*.js "$SRC"/init/cast.js 2>/dev/null | cksum | cut -d' ' -f1)"

# sed 的替换串里转义 & 和 |
esc() { printf '%s' "$1" | sed 's/[&|]/\\&/g'; }
B="$(esc "$BASE")"

rewrite() { # $1 源文件  $2 目标文件  $3 本页自身路径（/、/en 或 /init）
  local self; self="$(esc "$BASE${3%/}")"
  sed -E \
    -e "s|https://SITE_DOMAIN/en/|https://SITE_DOMAIN$B/en|g" \
    -e "s|https://SITE_DOMAIN/init/|https://SITE_DOMAIN$B/init|g" \
    -e "s|https://SITE_DOMAIN/og\.png|https://SITE_DOMAIN$B/og.png|g" \
    -e "s|https://SITE_DOMAIN/\"|https://SITE_DOMAIN$B\"|g" \
    -e "s#(href|src)=\"(\.\./)?assets/#\1=\"$B/assets/#g" \
    -e "s#href=\"(\.\./)?favicon\.svg\"#href=\"$B/favicon.svg\"#g" \
    -e "s#href=\"\./\"#href=\"$self\"#g" \
    -e "s#href=\"\.\./\"#href=\"$B\"#g" \
    -e "s#href=\"\.\./\##href=\"$B\##g" \
    -e "s#href=\"(\.\./)?init/\"#href=\"$B/init\"#g" \
    -e "s#src=\"cast\.js\"#src=\"$B/init/cast.js\"#g" \
    -e "s#(\"$B/(assets/[^\"]+\\.(css|js)|init/cast\\.js))\"#\\1?v=$VER\"#g" \
    -e "s#href=\"en/\"#href=\"$B/en\"#g" \
    "$1" > "$2"
  if [ -n "$DOMAIN" ]; then
    sed -i.bak "s|SITE_DOMAIN|$(esc "$DOMAIN")|g" "$2" && rm -f "$2.bak"
  fi
}
rewrite "$SRC/index.html"    "$OUT/index.html"    "/"
rewrite "$SRC/en/index.html" "$OUT/en/index.html" "/en"
rewrite "$SRC/init/index.html" "$OUT/init/index.html" "/init"

# 检查：不应再有相对的资源路径
if grep -nE '(href|src)="(\.\./|\./|assets/|en/|init/|cast\.js|favicon)' "$OUT/index.html" "$OUT/en/index.html" "$OUT/init/index.html"; then
  echo "警告：上面这些路径没有改写，请检查。" >&2
fi

cat <<EOF
已复制到 $OUT

还差一步：在 next.config 里加上 rewrites，让 $BASE、$BASE/en 和 $BASE/init 指向静态页面。
如果已经有 rewrites，把这三条并进去即可：

  async rewrites() {
    return {
      beforeFiles: [
        { source: '$BASE', destination: '$BASE/index.html' },
        { source: '$BASE/en', destination: '$BASE/en/index.html' },
        { source: '$BASE/init', destination: '$BASE/init/index.html' },
      ],
    };
  },

然后 npm run dev，打开 http://localhost:3000$BASE
EOF
