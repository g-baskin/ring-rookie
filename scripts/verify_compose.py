#!/usr/bin/env python3
"""Validate Compose and the bounded full-stack smoke test."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run("docker", "compose", "config", "--quiet")
    run("docker", "compose", "up", "-d", "--wait")
    run("python3", "scripts/smoke_stack.py", "--timeout", "180")
    print("PASSED Compose config and bounded full-stack smoke")


if __name__ == "__main__":
    main()
