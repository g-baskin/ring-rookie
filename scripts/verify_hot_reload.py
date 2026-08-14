#!/usr/bin/env python3
"""Verify source reload remains available during a production build."""

from pathlib import Path
import subprocess
import time
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


def started_at(container: str) -> str:
    return subprocess.run(
        ["docker", "inspect", "-f", "{{.State.StartedAt}}", container],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def fetch(url: str) -> None:
    last_error: Exception | None = None
    for _ in range(10):
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status != 200:
                    raise RuntimeError(f"{url} returned {response.status}")
                response.read()
                return
        except Exception as error:
            last_error = error
            time.sleep(1)
    raise RuntimeError(f"{url} remained unavailable") from last_error


def main() -> None:
    subprocess.run(["docker", "compose", "up", "-d", "--wait"], cwd=ROOT, check=True)
    before = {
        "backend": started_at("ring-rookie-backend"),
        "frontend": started_at("ring-rookie-frontend"),
    }
    (ROOT / "backend/app/api/health.py").touch()
    (FRONTEND / "src/app/login/page.tsx").touch()

    build = subprocess.Popen(["npm", "run", "build"], cwd=FRONTEND)
    requests = 0
    while build.poll() is None:
        fetch("http://localhost:8000/health/ready")
        fetch("http://localhost:4173/login")
        requests += 2
        time.sleep(1)
    if build.wait() != 0:
        raise RuntimeError("production build failed")

    time.sleep(5)
    fetch("http://localhost:8000/health/ready")
    fetch("http://localhost:4173/login")
    if started_at("ring-rookie-backend") != before["backend"]:
        raise RuntimeError("backend container restarted")
    if started_at("ring-rookie-frontend") != before["frontend"]:
        raise RuntimeError("frontend container restarted")
    if not (FRONTEND / ".next-dev").is_dir() or not (FRONTEND / ".next-build").is_dir():
        raise RuntimeError("Next.js artifacts are not isolated")
    print(f"PASSED concurrent build and hot reload ({requests} requests)")


if __name__ == "__main__":
    main()
