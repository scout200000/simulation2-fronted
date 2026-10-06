# Simulation2 Frontend

独立于 `Simulation2` 仓库运行的 Vite + Vue 3 前端项目，包含 V1 和 V2 两套控制台。

## 页面入口

```text
index.html  项目入口页
v1.html     V1 完整控制台
v2.html     V2 单屏控制台
```

## 一键启动

直接双击 `start.py` 即可。脚本会自动：

- 检测并复用已经在运行的后端；
- 必要时启动 `D:\Simulation2\demo\api_server.py`；
- 启动本项目 Vite 开发服务器；
- 自动选择可用端口并打开浏览器；
- 按 `Ctrl+C` 时同时停止本次启动的前后端进程。

如果后端不在默认目录，可以在系统环境变量中设置：

```text
SIMULATION2_BACKEND=D:\Simulation2
SIMULATION2_BACKEND_PORT=8770
SIMULATION2_FRONTEND_PORT=5173
```

## 安装与启动

```powershell
pnpm install
pnpm run dev
```

默认地址：

```text
http://127.0.0.1:5173
```

Vite 会把 `/api` 请求代理到 `VITE_BACKEND_PROXY`，默认是：

```text
http://127.0.0.1:8770
```

可复制 `.env.example` 为 `.env` 修改后端地址。生产构建时，也可以设置：

```text
VITE_API_BASE_URL=https://backend.example.com
```

## 构建

```powershell
pnpm run build
pnpm run preview
```

构建产物位于 `dist/`，包含入口页、V1 和 V2 三个 HTML 入口。

项目运行时不读取 `Simulation2` 目录。V1/V2 的 API 请求统一通过
`VITE_BACKEND_PROXY` 或 `VITE_API_BASE_URL` 指向外部后端。
