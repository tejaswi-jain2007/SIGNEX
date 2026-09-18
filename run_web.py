"""
Master Launcher for NTRO SIGINT React + FastAPI Web Application.
Spawns FastAPI backend (port 8000) and Vite React frontend (port 5173).
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = os.path.join(str(PROJECT_ROOT), "frontend")

def launch_web(host: str = "127.0.0.1", api_port: int = 8000, web_port: int = 5173, auto_open: bool = True):
    print("=" * 70)
    print("STARTING NTRO SIGINT WEB WORKSTATION (REACT + FASTAPI)")
    print("=" * 70)
    print(f"[*] API Backend  : http://{host}:{api_port}")
    print(f"[*] React Client : http://{host}:{web_port}")
    print("[*] Air-Gap Mode : ACTIVE / AIR-GAPPED WORKSTATION")
    print("=" * 70)

    # 1. Start FastAPI server
    backend_cmd = [sys.executable, "-m", "uvicorn", "ntro_sigint.server.app:app", "--host", host, "--port", str(api_port)]
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(PROJECT_ROOT))
    print("[+] FastAPI backend process spawned (PID: {})".format(backend_proc.pid))

    time.sleep(1.5)

    # 2. Start Vite frontend server
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_cmd = [npm_cmd, "run", "dev", "--", "--port", str(web_port)]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR)
    print("[+] React Vite dev server spawned (PID: {})".format(frontend_proc.pid))

    # 3. Automatically open browser
    if auto_open:
        time.sleep(1.5)
        web_url = f"http://localhost:{web_port}"
        print(f"[*] Opening browser to {web_url} ...")
        webbrowser.open(web_url)

    print("\n[READY] Press Ctrl+C in this terminal to shut down both servers.\n")

    try:
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down NTRO SIGINT Web servers...")
    finally:
        frontend_proc.terminate()
        backend_proc.terminate()
        print("All processes stopped safely.")

if __name__ == "__main__":
    launch_web()
