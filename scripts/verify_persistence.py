#!/usr/bin/env python3
"""Verify PostgreSQL and Redis data survive service restarts."""

from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
MARKER = f"persistence-{time.time_ns()}"


def run(*command: str, capture: bool = False) -> str:
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=capture,
        text=True,
    )
    return result.stdout.strip() if result.stdout is not None else ""


def main() -> None:
    run("docker", "compose", "up", "-d", "--wait")
    run(
        "docker", "compose", "exec", "-T", "postgres", "psql", "-U", "postgres",
        "-d", "ringrookie", "-v", "ON_ERROR_STOP=1", "-c",
        "CREATE TABLE IF NOT EXISTS _ha_persistence_smoke (value text primary key)",
    )
    run(
        "docker", "compose", "exec", "-T", "postgres", "psql", "-U", "postgres",
        "-d", "ringrookie", "-v", "ON_ERROR_STOP=1", "-c",
        f"INSERT INTO _ha_persistence_smoke(value) VALUES ('{MARKER}')",
    )
    run("docker", "compose", "exec", "-T", "redis", "redis-cli", "SET", "ha-persistence-smoke", MARKER)
    run("docker", "compose", "restart", "postgres", "redis")
    run("docker", "compose", "up", "-d", "--wait")

    postgres_value = run(
        "docker", "compose", "exec", "-T", "postgres", "psql", "-U", "postgres",
        "-d", "ringrookie", "-Atc",
        f"SELECT value FROM _ha_persistence_smoke WHERE value='{MARKER}'", capture=True,
    )
    redis_value = run(
        "docker", "compose", "exec", "-T", "redis", "redis-cli", "GET",
        "ha-persistence-smoke", capture=True,
    ).replace("\r", "")
    if postgres_value != MARKER or redis_value != MARKER:
        raise RuntimeError("persistent data was lost")

    run(
        "docker", "compose", "exec", "-T", "postgres", "psql", "-U", "postgres",
        "-d", "ringrookie", "-v", "ON_ERROR_STOP=1", "-c",
        f"DELETE FROM _ha_persistence_smoke WHERE value='{MARKER}'",
    )
    run("docker", "compose", "exec", "-T", "redis", "redis-cli", "DEL", "ha-persistence-smoke")
    run("python3", "scripts/smoke_stack.py", "--timeout", "120")
    print("PASSED volume persistence")


if __name__ == "__main__":
    main()
