# Dojo 迁入后的当前启动方式

从 Dojo 根执行 `uv sync --group visualization`，前端依赖使用 `npm ci --prefix packages/ai4e-viz/frontend`，构建使用对应 `npm run ... build`。独立应用启动 `uv run ai4e-vis --context /absolute/context.json`；旧三服务示例启动器使用 `uv run python packages/ai4e-viz/run_project.py start`。Python 3.12，backend/requirements.txt 仅历史基线。配置及输出写明确项目任务，运行缓存默认用户缓存目录。下面保留原仓库历史便携说明，原 .venv/var 安装命令不作为 Dojo 当前依赖入口。

# AI4E_Vis 便携包迁移与启动指南

本文档适用于便携包 `AI4E_Vis-portable-20260826.zip`，用于在新的 macOS 或 Linux 电脑上恢复 AI4E VizReport 数据可视化平台。

便携包已包含：

- React 前端、FastAPI 后端、Trame/vtk.js 和 Online3DViewer 源码。
- 数据资产、案例 fixture、已上传文件、报告正文和 Spec。
- SQLite 数据库的一致快照。
- npm 锁定文件、Python 依赖清单和 Quarto 校验安装脚本。

便携包不包含 `.venv`、`node_modules`、Quarto 本机二进制、Chromium 和可重建的报告导出。这些内容与操作系统和 CPU 架构有关，必须在新电脑上重新安装。

## 1. 支持的系统

推荐：

- macOS 13 或更高版本，Apple Silicon 或 Intel。
- Linux x86_64 或 ARM64，推荐 Ubuntu 22.04/24.04。
- Python 3.11–3.13，推荐 Python 3.13。
- Node.js 24.15.0 或更高的 24.x LTS 与 npm；也支持 Node.js 22.22.2 或更高的 22.x。
- 至少 5 GB 可用空间，推荐预留 8 GB。

Windows 原生环境不是当前启动器的支持目标；Windows 电脑请使用 WSL2 Ubuntu，并按 Linux 步骤安装。

## 2. 解压便携包

将 ZIP 复制到新电脑。以放在“下载”目录为例：

```bash
mkdir -p "$HOME/AI4E"
cd "$HOME/AI4E"
unzip "$HOME/Downloads/AI4E_Vis-portable-20260826.zip"
cd AI4E_Vis
```

解压后应能看到：

```text
AI4E_Vis/
├── backend/
├── frontend/
├── docs/
├── run_project.py
└── README.md
```

确认终端当前位于项目根目录：

```bash
pwd
ls run_project.py backend/requirements.txt frontend/package-lock.json
```

## 3. 检查基础软件

```bash
python3 --version
node --version
npm --version
```

期望结果：

- Python 不低于 3.11。
- Node.js 推荐为 24.15.0 或更高的 24.x；使用 22.x 时不得低于 22.22.2。当前前端锁定的 `jsdom 30.0.1` 不支持 Node 24.14 及更早版本，也不支持 Node 20。
- npm 可正常运行。

macOS 可通过 Homebrew 安装 Python 和 Node.js；Linux 可使用系统包管理器、nvm 或所在组织的标准运行时。安装后重新打开终端，再执行上述版本检查。

Linux 还建议先安装中文字体：

```bash
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk
```

## 4. 安装 Python 后端依赖

在项目根目录执行：

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install --upgrade pip
backend/.venv/bin/python -m pip install -r backend/requirements.txt
```

该步骤会安装 VTK、Trame、FastAPI、PyArrow、Trimesh、Pillow 等后端依赖，下载和安装时间取决于网络和电脑性能。

验证 Python 环境：

```bash
backend/.venv/bin/python -c "import fastapi, vtk, trame, pyarrow; print('Python dependencies OK')"
```

## 5. 安装前端依赖和报告导出浏览器

### 5.1 安装前端依赖（必需）

为避免新电脑已有的 `~/.npm` 缓存权限或残留文件影响安装，本项目首次安装固定使用一个独立缓存目录。以下命令同时适用于 macOS 和 Linux，请整段执行，不要改回单独运行 `npm ci`：

```bash
cd frontend
QODER_NPM_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/qoder-npm"
mkdir -p "$QODER_NPM_CACHE"
npm_config_cache="$QODER_NPM_CACHE" npm config get cache
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm_config_cache="$QODER_NPM_CACHE" npm ci
test -d node_modules && echo "前端依赖安装成功"
cd ..
```

`npm config get cache` 的输出应以 `/qoder-npm` 结尾。`npm ci` 会严格按 `package-lock.json` 恢复 ECharts、Perspective、Plotly、Vega、React Flow 和 Online3DViewer 等前端依赖。这里设置 `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`，避免安装前端依赖时同时下载约 180 MiB 的 Chromium；Chromium 不是启动平台的前置条件。

安装日志中的 `deprecated` 或 `ERESOLVE overriding peer dependency` 通常只是上游依赖警告。以命令退出状态和最后的“前端依赖安装成功”为准；如果出现 `npm error`、`EACCES`、`EEXIST` 或没有生成 `node_modules`，请按第 10.2 节处理。

### 5.2 安装报告导出浏览器（按需）

只有需要下载“当前报告”的 HTML/PDF，或运行 Playwright 端到端测试时，才需要安装 Chromium：

```bash
cd frontend
QODER_NPM_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/qoder-npm"
npm_config_cache="$QODER_NPM_CACHE" npx playwright install chromium
cd ..
```

Linux 如果 Chromium 缺少系统库，改用：

```bash
cd frontend
QODER_NPM_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/qoder-npm"
npm_config_cache="$QODER_NPM_CACHE" npx playwright install --with-deps chromium
cd ..
```

Chromium 用于将当前 React 报告阅读页冻结为自包含 HTML 和 PDF。不安装 Chromium 不会影响项目启动、数据上传、推荐和可视化，但“下载当前报告”会显示浏览器运行时不可用。不要为了普通启动执行 `npx playwright install`。

## 6. 安装固定版本 Quarto

执行：

```bash
backend/.venv/bin/python backend/scripts/install_quarto.py
backend/.tools/quarto/1.10.18/bin/quarto --version
```

如果之前的旧安装进程长时间没有输出，可按 `Control+C` 终止，然后重新执行上述命令。新版脚本会：

- 在 Quarto 1.10.18 已正确安装时立即返回，不重复下载。
- 下载时每秒显示 MiB、百分比和速度。
- 连接超时后最多重试 3 次，不再无限等待。
- 同时兼容 Python 3.11 和更新版本的安全 tar 解压 API。

高延迟网络可放宽超时并增加重试次数：

```bash
backend/.venv/bin/python backend/scripts/install_quarto.py --timeout 120 --retries 5
```

期望输出：

```text
1.10.18
```

安装脚本会根据 macOS/Linux 和 CPU 架构下载官方 Quarto 1.10.18，验证 SHA-256 后安装到 `backend/.tools/quarto/1.10.18/`。

如果新电脑无法访问 GitHub，可以在另一台电脑下载对应平台的官方 `quarto-1.10.18-*.tar.gz`，复制到新电脑后执行：

```bash
backend/.venv/bin/python backend/scripts/install_quarto.py --archive "/path/to/quarto-1.10.18-platform.tar.gz"
```

Quarto 用于用户编排报告的 HTML/PDF 导出。Quarto 缺失时，其他服务仍可启动，但 Quarto 导出会显示不可用。

## 7. 首次启动全部服务

确保仍位于 `AI4E_Vis` 项目根目录，然后执行：

```bash
backend/.venv/bin/python run_project.py start
```

成功时会显示三个 `ready`：

```text
[ready] 解析 / 推荐 API        http://127.0.0.1:8091/api/health
[ready] Trame + vtk.js     http://127.0.0.1:8090/
[ready] React + Vite       http://127.0.0.1:5275/
```

打开浏览器：

- 平台首页：<http://127.0.0.1:5275/>
- Miller 时序场报告：<http://127.0.0.1:5275/#/reports/rep-miller-tokamak-timeseries>
- G-S 审计报告：<http://127.0.0.1:5275/#/reports/rep-gs-pino-2026-0823>
- 聚变站 GEO 案例：<http://127.0.0.1:5275/#/assets/A-1114>

三个服务只监听 `127.0.0.1`，默认不向局域网或公网开放。

## 8. 启动后验证

检查进程与 HTTP 状态：

```bash
backend/.venv/bin/python run_project.py status
curl http://127.0.0.1:8091/api/health
curl http://127.0.0.1:8091/api/renderer-health
curl http://127.0.0.1:8091/api/quarto/health
```

建议手动检查以下链路：

1. 进入“数据资产”，确认内置案例和上传记录存在。
2. 打开 Miller 报告，点击“播放”，确认 VTK 曲面场的帧号和颜色随时间变化。
3. 打开 GEO 案例，确认 Online3DViewer 可旋转、缩放和重置视角。
4. 在报告右上角选择“下载当前报告 HTML”或“PDF”，确认导出任务成功。

便携包不保留旧电脑的导出任务历史，因为这些记录指向旧电脑的绝对路径。报告正文、草稿、冻结版本和数据均已保留；在新电脑首次点击导出时会生成新记录。

## 9. 日常启动、停止和重启

完成首次安装后，日常只需在项目根目录执行：

```bash
backend/.venv/bin/python run_project.py start
```

查看状态：

```bash
backend/.venv/bin/python run_project.py status
```

重启：

```bash
backend/.venv/bin/python run_project.py restart
```

停止：

```bash
backend/.venv/bin/python run_project.py stop
```

启动器会记录自己创建的进程，不会主动终止不属于本项目的外部进程。

## 10. 日志与常见故障

日志目录：

```text
var/runtime/
```

查看最新日志：

```bash
tail -n 80 var/runtime/api.log
tail -n 80 var/runtime/trame.log
tail -n 80 var/runtime/frontend.log
```

### 10.1 提示 `.venv` 或 `node_modules` 不存在

这表示尚未完成首次安装。重新执行第 4–5 节。

### 10.2 `npm ci` 报 `EACCES`、`EEXIST` 或缓存权限错误

如果错误路径位于 `~/.npm/_cacache`，说明是当前电脑的 npm 默认缓存权限异常或内容损坏，并非项目依赖缺失。常见原因是以前运行过 `sudo npm ...`，使缓存中的部分文件归 root 所有。

不要使用 `sudo npm ci`、`npm ci --force`，也不要直接删除整个 `~/.npm`。回到 `frontend` 目录，使用本指南约定的独立缓存重试：

```bash
cd frontend
QODER_NPM_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/qoder-npm"
mkdir -p "$QODER_NPM_CACHE"
npm_config_cache="$QODER_NPM_CACHE" npm config get cache
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm_config_cache="$QODER_NPM_CACHE" npm ci
test -d node_modules && echo "前端依赖安装成功"
cd ..
```

如果仍失败，保留完整输出并检查最后 50 行：

```bash
cd frontend
QODER_NPM_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/qoder-npm"
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm_config_cache="$QODER_NPM_CACHE" npm ci 2>&1 | tail -50
cd ..
```

个人电脑上也可以选择永久修复默认缓存的所有权，然后验证缓存；这不是项目启动的必需步骤：

```bash
sudo chown -R "$(id -u)":"$(id -g)" "$HOME/.npm"
npm cache verify
```

如果同时看到 `EBADENGINE`，先检查 `node --version`。Node 24 必须升级到 24.15.0 或更高版本，或者改用 22.22.2 或更高版本，然后重新执行第 5.1 节。

### 10.3 `npm ci` 报 package.json 与 package-lock.json 不同步

如果出现 `npm error code EUSAGE`，并列出 `Missing: @esbuild/... from lock file`，说明使用的是修复前的便携包锁文件。新版便携包已经补齐 Vitest/Vite 所需的跨平台 esbuild 条目。旧目录无需重新复制数据，可在 `frontend` 中执行一次普通安装来修复本机锁文件并完成安装：

```bash
cd frontend
QODER_NPM_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/qoder-npm"
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm_config_cache="$QODER_NPM_CACHE" npm install
test -x node_modules/.bin/vite && echo "Vite 安装成功"
cd ..
```

只有看到“Vite 安装成功”后才能运行 `run_project.py start`。这里的 `npm install` 是旧便携包的一次性迁移步骤；使用当前便携包进行全新安装时，仍按第 5.1 节执行确定性的 `npm ci`。

### 10.4 5275、8090 或 8091 端口被占用

先查看状态：

```bash
backend/.venv/bin/python run_project.py status
lsof -nP -iTCP:5275 -sTCP:LISTEN
lsof -nP -iTCP:8090 -sTCP:LISTEN
lsof -nP -iTCP:8091 -sTCP:LISTEN
```

如果是旧的 AI4E_Vis 进程，使用 `run_project.py stop` 后再启动。如果是其他程序，请先关闭该程序；不要盲目终止未知进程。

### 10.5 Trame/vtk.js 显示离线

检查：

```bash
curl http://127.0.0.1:8090/
tail -n 120 var/runtime/trame.log
```

常见原因是 VTK/Trame 依赖未安装完整，或 8090 端口被占用。可重新执行：

```bash
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python run_project.py restart
```

### 10.6 HTML/PDF 导出失败

先检查：

```bash
curl http://127.0.0.1:8091/api/quarto/health
cd frontend
QODER_NPM_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/qoder-npm"
npm_config_cache="$QODER_NPM_CACHE" npx playwright install chromium
cd ..
```

再查看 `var/runtime/api.log` 以及导出任务返回的 Quarto/浏览器日志。Linux 中文缺字时，安装 `fonts-noto-cjk` 后重新导出。

如果 Quarto 安装停在下载阶段，先按 `Control+C`，然后重试：

```bash
backend/.venv/bin/python backend/scripts/install_quarto.py --timeout 120 --retries 5
```

如果报错 `extractall() got an unexpected keyword argument 'filter'`，表示当前目录仍是旧版安装脚本。请从最新便携包中替换 `backend/scripts/install_quarto.py`，然后重新运行；不需要重新复制数据库或数据资产。

仍然失败通常表示 `release-assets.githubusercontent.com` 被当前网络或代理阻断。请改用第 6 节的 `--archive` 离线安装；不要使用未经信任的重打包文件，脚本会校验官方 SHA-256。

### 10.7 前端页面打开但 API 请求失败

确认 API 返回 HTTP 200：

```bash
curl -i http://127.0.0.1:8091/api/health
```

然后使用 `run_project.py restart` 同时重启前后端，不要只单独启动 Vite。

## 11. 可选回归测试

如果需要确认新电脑的环境与开发基线一致，可执行：

```bash
cd backend
.venv/bin/python -m pytest tests -q
cd ../frontend
npm test -- --run
npm run build
cd ..
```

浏览器端到端测试会额外启动隔离端口：

```bash
cd frontend
npx playwright test
cd ..
```

## 12. 磁盘占用与后续迁移

便携 ZIP 约 162 MiB，解压后的源码与业务数据约 238 MiB。安装 VTK/Python 环境、前端渲染器、Chromium 和 Quarto 后，项目目录占用约 2.2 GB，这是完整科学可视化运行时的正常体积。

可先查看无损清理计划：

```bash
backend/.venv/bin/python backend/scripts/maintenance.py
```

清理前先停止服务，再删除可重建缓存和旧导出：

```bash
backend/.venv/bin/python run_project.py stop
backend/.venv/bin/python backend/scripts/maintenance.py --apply
backend/.venv/bin/python run_project.py start
```

如果需要再次迁移到第三台电脑，将输出路径设在项目目录之外：

```bash
backend/.venv/bin/python run_project.py stop
backend/.venv/bin/python backend/scripts/create_portable_bundle.py \
  --output "$HOME/Desktop/AI4E_Vis-portable.zip"
```

该脚本会对 SQLite 执行在线一致备份，并在 ZIP 内生成 `portable-manifest.json`，其中记录每个文件的大小和 SHA-256。
