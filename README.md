# aibox 宣传站

**简体中文** | [English](README.en.md)

aibox 的单页宣传网站：中文主页 + 英文版，纯静态，无构建步骤、无依赖、无追踪脚本，也不请求任何第三方资源（字体用系统字体）。

网站的核心定位是：让 Claude Code 在独立的 Docker 环境中通过远程节点联网，减少真实公网 IP、宿主机系统信息与个人配置被工具获取或随请求暴露，以降低相关账号风控与封号风险为目标。Codex 等终端工具也可使用。

中英文页面、分享卡片与录制页同步说明保护范围：提供网络与文件隔离，不保证防封号，也不提供完整机器指纹伪装。内核与 CPU 信息、授权文件中的身份信息、工具遥测和账号标识仍可能存在；浏览器登录与初始化、构建、订阅和检测流量需区分。

网站和 aibox 产品代码分开存放：本目录只放网站；aibox 仓库默认在 `~/claude/Linux-terminal`（只有录制脚本需要用到它）。

```
Linux-terminal-web/
├── README.md         中文说明
├── README.en.md      英文说明
├── index.html        中文主页
├── en/index.html     英文版
├── init/             ./aibox init 的真实录制回放页（cast.js 是录制数据）
├── assets/site.css   样式（颜色都在 :root 里，深色/浅色跟随系统）
├── assets/site.js    顶栏、复制按钮、首屏终端演示
├── assets/cast-player.js  终端录制回放器（不是视频，文字可复制）
├── favicon.svg
├── og.svg            分享卡片图的源文件（需导出为 og.png，见下文）
├── robots.txt
├── nextjs/sync.sh    接入已有 Next.js 站点用的同步脚本
└── tools/record-init.py  录制 ./aibox init 并生成 init/cast.js
```

## 本地预览

任选其一，然后打开 http://localhost:8000/ ：

```bash
cd ~/claude/Linux-terminal-web && python3 -m http.server 8000
```

```bash
npx serve . -l 8000
```

直接双击 `index.html` 也能看，但复制按钮在 `file://` 下会改用兼容方式。

## 上线前要替换的占位符

| 占位符 | 位置 | 替换为 |
|---|---|---|
| `SITE_DOMAIN` | canonical、hreflang、og:url | 网站域名（含子路径，例如 `owner.github.io/aibox`） |
| `LICENSE_NAME` | 页脚 | 协议名，例如 `MIT`；仓库里也需要补一个 `LICENSE` 文件 |

一次性替换（GNU sed；macOS 上把 `sed -i` 换成 `sed -i ''`）：

```bash
sed -i 's#SITE_DOMAIN#aibox.example.com#g; s#LICENSE_NAME#MIT#g' index.html en/index.html init/index.html
```

## 分享卡片图（og.png）

社交平台大多不支持 SVG 预览图。用任意工具把 `og.svg` 导出成 1200×630 的 `og.png` 放在本目录下，再取消两个页面 `<head>` 里 `og:image` 和 `twitter:card` 两行的注释。例如：

```bash
rsvg-convert -w 1200 -h 630 og.svg -o og.png
```

## 部署

站点就是本目录，任何静态托管都可以。`README.md`、`README.en.md`、`nextjs/` 和 `tools/` 是维护用的，发布出去也没有影响，介意的话在托管平台上排除它们。

**GitHub Pages**：仓库 Settings → Pages → Source 选 “GitHub Actions”，添加 `.github/workflows/pages.yml`：

```yaml
name: pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: github-pages
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - uses: actions/deploy-pages@v4
```

**Cloudflare Pages**：连接仓库，构建命令留空，输出目录留空（仓库根目录）。

**Vercel**：导入仓库，Framework 选 “Other”，Root Directory 留空，构建命令留空。

**Netlify**：Base directory 和 Publish directory 都留空（仓库根目录），构建命令留空。

## 接入已有的 Next.js 站点

页面以独立子页面的形式挂在 Next.js 站点下（默认 `/aibox`、`/aibox/en` 和录制页 `/aibox/init`）。它保持静态 HTML，自带 CSS 和 JS，不经过站点的 layout，所以不会受全局样式影响，也不会影响站点其他页面。

**1. 复制页面到 Next.js 项目**（会覆盖 `public/aibox/`）：

```bash
bash ~/claude/Linux-terminal-web/nextjs/sync.sh /path/to/your-next-app
```

脚本把文件复制到 `public/aibox/`，并把页面里的相对路径改成 `/aibox/...`。想换路径用 `--base /tools/aibox`；想顺便填上域名用 `--domain example.com`。本目录不会被修改，以后改了内容重新运行一次即可。

**2. 在 `next.config.ts`（或 `.js` / `.mjs`）里加 rewrites：**

```ts
const nextConfig = {
  // ……原有配置
  async rewrites() {
    return {
      beforeFiles: [
        { source: '/aibox', destination: '/aibox/index.html' },
        { source: '/aibox/en', destination: '/aibox/en/index.html' },
        { source: '/aibox/init', destination: '/aibox/init/index.html' },
      ],
    };
  },
};
```

如果原来已有 `rewrites()`：它返回数组时，那个数组相当于 `afterFiles`，改成 `{ beforeFiles: [上面几条], afterFiles: [原数组] }`；返回对象时，把这几条加进 `beforeFiles`。

**3. 运行：**

```bash
cd /path/to/your-next-app
npm run dev
```

打开 http://localhost:3000/aibox 。

已在 Next.js 16.4 新项目里验证过：开发模式和 `next build && next start` 下中英文页面、语言切换、锚点跳转、样式和脚本都正常，没有 404 和脚本错误。

注意：

- 站点设置了 `basePath`（比如 `/blog`）时，用 `--base /blog/aibox` 运行脚本，rewrites 里仍写 `/aibox`。
- 站点有 middleware（比如做多语言跳转或登录拦截）时，要在 `matcher` 里排除 `/aibox`，否则页面可能被重定向。
- 站点用 `output: 'export'` 静态导出时，rewrites 不生效；导出目录里 `aibox/index.html` 由静态托管直接提供，访问 `/aibox/` 即可。
- 想在站点导航里加入口，用普通链接 `<a href="/aibox">`。它是静态页，不是 Next.js 路由，用 `next/link` 没有好处，只会多一次失败的客户端跳转。

## 重新录制 ./aibox init

录制页 `init/` 回放的是一次真实运行的 `./aibox init`。aibox 的向导或输出改了之后，重新录一次：

```bash
mkdir -p ~/code/myapp ~/code/specs && git -C ~/code/myapp init -q   # 向导里要授权的两个示例目录（myapp 是 git 项目，向导才会列出）
printf '%s\n' "你的订阅链接" > /tmp/sub.txt
cd ~/claude/Linux-terminal-web
python3 tools/record-init.py --sub-file /tmp/sub.txt          # aibox 不在 ~/claude/Linux-terminal 时加 --aibox <路径>
rm /tmp/sub.txt
```

- 录制是真实的：会在 aibox 仓库里写入 `config/`、构建镜像、启动容器，和手动运行 `./aibox init` 一样。想从零开始录，先在 aibox 仓库里 `./aibox destroy` 并删除 `config/`。
- 脚本在伪终端（100×32）里输入命令、按提示作答：选项 1 → 粘贴链接 → 全部节点 → 选编号 1 的项目（`~/code/myapp`，允许修改）→ 输入 `~/code/specs`（只读）→ 不安装命令 → 立即启动。没有预设的 [Y/n] 问题一律回车采用默认值。
- 订阅里排在前面的是 AI 服务不支持地区的节点时，向导会提醒并停下，加 `--filter '日本|JP'` 这样的节点关键词再录。项目文件夹可以用 `--mount 编号或路径:y|n` 指定。
- 生成 `init/cast.js` 前会脱敏：节点链接只保留协议名，公网 IPv4 换成 203.0.113.x 等文档保留地址，IPv6 换成 2001:db8::；运营商名称用 `--redact '原文=替换'` 指定。如果结果里还能找到链接的片段，脚本会报错，不生成文件。
- 未脱敏的原始录制保存在 aibox 仓库的 `.aibox/init-raw.cast.json`（那里已被 .gitignore 忽略，不会进本目录），只想调整脱敏规则时用 `--remask` 重新生成，不用再跑一遍。
- 发布前打开 `init/` 页面看一遍，确认没有不想公开的信息（例如节点名称里的服务商名字）。

## 修改内容时注意

- `README.md` 为默认中文入口，`README.en.md` 为英文版；修改说明时同步两份文档，并保留顶部的语言切换链接。
- 两个页面结构相同，改一处时记得同步另一处。
- 页面上的事实以 aibox 仓库的 `README.md`、`docs/` 和 `AGENTS.md` 为准。未实测的环境（真实 Mac、SELinux、rootless Docker）不要写成“已验证”。
- 防止真实环境暴露、降低相关账号风控与封号风险是设计目标，不能写成已经验证的防封号效果；不要宣传完整机器指纹伪装或抹除遥测与账号标识。
- 终端演示里的出口 IP 都是文档保留地址（203.0.113.x、198.51.100.x），换成真实录屏前先遮掉 IP 和订阅链接。
- 首屏终端动画的脚本在页面里的 `<script type="application/json" id="demo-script">`，`<pre id="demo">` 里是关闭动效或没有 JS 时显示的最终画面，两者要一致。
- 不要引入 Google Fonts、统计脚本等第三方资源；页脚写了“不请求第三方资源”。
