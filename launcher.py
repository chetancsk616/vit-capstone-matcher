from __future__ import annotations

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def find_available_port(start: int = 8501, attempts: int = 50) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No available local port found for Streamlit.")


def open_browser_later(port: int) -> None:
    time.sleep(2.5)
    webbrowser.open_new(f"http://localhost:{port}")


def main() -> None:
    app_path = resource_path("app.py")
    if not app_path.exists():
        raise FileNotFoundError(f"Bundled Streamlit app was not found: {app_path}")

    port = find_available_port()
    threading.Thread(target=open_browser_later, args=(port,), daemon=True).start()

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port),
        "--server.address",
        "localhost",
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--global.developmentMode",
        "false",
    ]

    from streamlit.web.cli import main as streamlit_main

    streamlit_main()


if __name__ == "__main__":
    main()
