#!/usr/bin/env python3
"""Verify frontend and backend restart into a healthy stack."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def inspect(container: str, template: str) -> str:
    return subprocess.run(
        ["docker", "inspect", "-f", template, container],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def main() -> None:
    subprocess.run([
        "docker", "compose", "up", "-d", "--wait", "--wait-timeout", "180"
    ], cwd=ROOT, check=True, timeout=240)
    before = {
        name: inspect(f"ring-rookie-{name}", "{{.State.StartedAt}}")
        for name in ("backend", "frontend")
    }
    subprocess.run(
        ["docker", "compose", "restart", "backend", "frontend"],
        cwd=ROOT,
        check=True,
        timeout=120,
    )
    subprocess.run([
        "docker", "compose", "up", "-d", "--wait", "--wait-timeout", "180"
    ], cwd=ROOT, check=True, timeout=240)
    for name in ("backend", "frontend"):
        container = f"ring-rookie-{name}"
        if inspect(container, "{{.State.Health.Status}}") != "healthy":
            raise RuntimeError(f"{name} did not recover")
        if inspect(container, "{{.State.StartedAt}}") == before[name]:
            raise RuntimeError(f"{name} did not restart")
    subprocess.run(
        ["python3", "scripts/smoke_stack.py", "--timeout", "120"],
        cwd=ROOT,
        check=True,
    )
    print("PASSED restart recovery")


if __name__ == "__main__":
    main()
