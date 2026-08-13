#!/usr/bin/env python3
"""Validate environment documentation without importing application settings."""

from __future__ import annotations
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = {"NODE_ENV", "CI", "VERCEL", "VERCEL_ENV"}
SECRET = re.compile(r"(?:SECRET|PASSWORD|TOKEN|API_KEY|PRIVATE_KEY|AUTH)", re.I)
UNSAFE = {
    "admin",
    "password",
    "secret",
    "changeme",
    "change-this-to-a-random-secret-key-in-production",
    "postgres",
}


def env_file(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k] = v
    return out


def backend_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Settings":
            names |= {
                n.target.id
                for n in node.body
                if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
            }
    return names


def frontend_names(root: Path) -> set[str]:
    pattern = re.compile(
        r"process\.env(?:\.([A-Z][A-Z0-9_]*)|\[['\"]([A-Z][A-Z0-9_]*)['\"]\])"
    )
    names = set()
    for p in root.rglob("*"):
        if p.suffix in {".ts", ".tsx", ".js", ".mjs"} and not (
            {"node_modules", ".next"} & set(p.parts)
        ):
            names |= {a or b for a, b in pattern.findall(p.read_text(errors="ignore"))}
    return names - SYSTEM


def validate() -> list[str]:
    errors = []
    checks = [
        (
            "backend",
            backend_names(ROOT / "backend/app/core/config.py"),
            env_file(ROOT / "backend/.env.example"),
        ),
        (
            "frontend",
            frontend_names(ROOT / "frontend"),
            env_file(ROOT / "frontend/.env.example"),
        ),
    ]
    for label, used, documented in checks:
        for name in sorted(used - set(documented)):
            errors.append(f"{label}: undocumented variable {name}")
        for name in sorted(set(documented) - used):
            errors.append(f"{label}: stale variable {name}")
        for name, value in documented.items():
            if name.startswith("NEXT_PUBLIC_") and SECRET.search(name):
                errors.append(f"{label}: public variable is secret-shaped: {name}")
            if SECRET.search(name) and value.strip().lower() in UNSAFE:
                errors.append(f"{label}: unsafe default for {name}")
    return errors


def main() -> int:
    errors = validate()
    for error in errors:
        print(error)
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
