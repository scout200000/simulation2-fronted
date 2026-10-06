#!/usr/bin/env python3
"""One-click launcher for the independent Simulation2 frontend."""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


FRONTEND_DIR = Path(__file__).resolve().parent
BACKEND_DIR = Path(
    os.environ.get("SIMULATION2_BACKEND", r"D:\Simulation2")
).resolve()
BACKEND_PORT = int(os.environ.get("SIMULATION2_BACKEND_PORT", "8770"))
FRONTEND_PORT_START = int(os.environ.get("SIMULATION2_FRONTEND_PORT", "5173"))
BACKEND_HEALTH_URL = (
    f"http://127.0.0.1:{BACKEND_PORT}/api/input/defaults"
)


def find_node() -> Path | None:
    candidates = [
        shutil.which("node"),
        str(
            Path.home()
            / ".cache"
            / "codex-runtimes"
            / "codex-primary-runtime"
            / "dependencies"
            / "node"
            / "bin"
            / "node.exe"
        ),
        r"C:\Program Files\nodejs\node.exe",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_file():
            return path
    return None


def find_package_manager() -> Path | None:
    candidates = [
        shutil.which("pnpm"),
        str(
            Path.home()
            / ".cache"
            / "codex-runtimes"
            / "codex-primary-runtime"
            / "dependencies"
            / "bin"
            / "fallback"
            / "pnpm.cmd"
        ),
        shutil.which("npm"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_file():
            return path
    return None


def python_has_requests(executable: Path) -> bool:
    try:
        result = subprocess.run(
            [str(executable), "-c", "import requests"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def find_backend_python() -> Path | None:
    candidates = [
        BACKEND_DIR / ".venv" / "Scripts" / "python.exe",
        Path(sys.executable),
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "python"
        / "python.exe",
        shutil.which("python"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.is_file() and python_has_requests(path):
            return path
    return None


def http_ok(url: str, timeout: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 500
    except (OSError, urllib.error.URLError):
        return False


def wait_http(url: str, process: subprocess.Popen | None, timeout: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if http_ok(url):
            return
        if process is not None and process.poll() is not None:
            raise RuntimeError(
                f"进程提前退出，退出码：{process.returncode}"
            )
        time.sleep(0.35)
    raise TimeoutError(f"等待服务超时：{url}")


def free_port(start: int, limit: int = 20) -> int:
    for port in range(start, start + limit):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"未找到可用端口：{start}-{start + limit - 1}")


def ensure_frontend_dependencies(node: Path) -> Path:
    vite_js = (
        FRONTEND_DIR
        / "node_modules"
        / "vite"
        / "bin"
        / "vite.js"
    )
    if vite_js.is_file():
        return vite_js

    package_manager = find_package_manager()
    if package_manager is None:
        raise RuntimeError(
            "未找到 pnpm/npm，且 node_modules 中也没有 Vite。"
        )
    print("首次运行，正在安装前端依赖……")
    subprocess.run(
        [str(package_manager), "install"],
        cwd=FRONTEND_DIR,
        check=True,
    )
    if not vite_js.is_file():
        raise RuntimeError("依赖安装完成，但仍未找到 Vite。")
    return vite_js


def terminate_process(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main() -> int:
    if not BACKEND_DIR.is_dir():
        print(f"后端目录不存在：{BACKEND_DIR}")
        print("可设置环境变量 SIMULATION2_BACKEND 指向后端目录。")
        return 1

    backend_process = None
    frontend_process = None
    try:
        if not http_ok(BACKEND_HEALTH_URL):
            backend_python = find_backend_python()
            if backend_python is None:
                raise RuntimeError("未找到可导入 requests 的 Python 解释器。")

            env = os.environ.copy()
            site_packages = BACKEND_DIR / ".venv" / "Lib" / "site-packages"
            if site_packages.is_dir():
                existing = env.get("PYTHONPATH", "")
                env["PYTHONPATH"] = (
                    str(site_packages)
                    if not existing
                    else str(site_packages) + os.pathsep + existing
                )

            print(f"启动后端：{backend_python}")
            backend_process = subprocess.Popen(
                [
                    str(backend_python),
                    "demo/api_server.py",
                    "--port",
                    str(BACKEND_PORT),
                ],
                cwd=BACKEND_DIR,
                env=env,
            )
            wait_http(BACKEND_HEALTH_URL, backend_process, timeout=25)
        else:
            print(f"复用已运行的后端：{BACKEND_HEALTH_URL}")

        node = find_node()
        if node is None:
            raise RuntimeError("未找到 Node.js。")

        vite_js = ensure_frontend_dependencies(node)
        frontend_port = free_port(FRONTEND_PORT_START)
        frontend_url = f"http://127.0.0.1:{frontend_port}"

        print(f"启动前端：{frontend_url}")
        frontend_process = subprocess.Popen(
            [
                str(node),
                str(vite_js),
                "--host",
                "127.0.0.1",
                "--port",
                str(frontend_port),
                "--strictPort",
            ],
            cwd=FRONTEND_DIR,
        )
        wait_http(frontend_url + "/", frontend_process, timeout=30)

        print()
        print("=" * 58)
        print(f"项目入口：{frontend_url}")
        print(f"V1 页面：{frontend_url}/v1.html")
        print(f"V2 页面：{frontend_url}/v2.html")
        print(f"后端接口：http://127.0.0.1:{BACKEND_PORT}/api")
        print("按 Ctrl+C 停止本次启动的前后端进程。")
        print("=" * 58)
        print()
        webbrowser.open(frontend_url)

        while True:
            if backend_process is not None and backend_process.poll() is not None:
                raise RuntimeError("后端进程已退出。")
            if frontend_process.poll() is not None:
                raise RuntimeError("前端进程已退出。")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务……")
        return 0
    except (OSError, RuntimeError, TimeoutError, subprocess.SubprocessError) as error:
        print(f"启动失败：{error}")
        return 1
    finally:
        terminate_process(frontend_process)
        terminate_process(backend_process)


if __name__ == "__main__":
    raise SystemExit(main())
