#!/usr/bin/env python3
# ruff: noqa: T201, S110, S607, PLR0912, ASYNC230, PTH110, PTH123
"""
Database Seed Data Management for Ring Rookie

This script handles seeding/syncing data across environments (local, QA, production).
It works with Docker containers and direct PostgreSQL connections.

Usage:
    # Export from local to seed file
    python scripts/seed_data.py export --env local --output seeds/agents.json

    # Import seed file to target environment
    python scripts/seed_data.py import --env production --input seeds/agents.json

    # Sync specific agent from local to production
    python scripts/seed_data.py sync --from local --to production --agent ag_IXqnWYBG

Environment variables:
    DATABASE_URL - Override database connection string
    LOCAL_DATABASE_URL - Local database (default: postgresql://postgres:postgres@localhost:5432/ringrookie)
    PROD_DATABASE_URL - Production database (from Railway)

Docker support:
    When running in Docker, set DATABASE_URL to the container's PostgreSQL connection.
    Example: DATABASE_URL=postgresql://postgres:postgres@db:5432/ringrookie
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

try:
    import asyncpg
except ImportError:
    print("Error: asyncpg not installed. Run: pip install asyncpg")
    sys.exit(1)


# Default connection strings
DEFAULT_LOCAL_DB = "postgresql://postgres:postgres@localhost:5432/ringrookie"
# Docker-compatible: use 'db' as hostname when running in container
DOCKER_LOCAL_DB = "postgresql://postgres:postgres@db:5432/ringrookie"


class UUIDEncoder(json.JSONEncoder):
    """JSON encoder that handles UUID and datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def get_database_url(env: str) -> str:
    """Get database URL for the specified environment."""
    if env_url := os.environ.get("DATABASE_URL"):
        return env_url.replace("postgresql+asyncpg://", "postgresql://")

    if env == "local":
        # Check if running in Docker
        if os.path.exists("/.dockerenv"):
            return os.environ.get("LOCAL_DATABASE_URL", DOCKER_LOCAL_DB)
        return os.environ.get("LOCAL_DATABASE_URL", DEFAULT_LOCAL_DB)

    if env == "production":
        prod_url = os.environ.get("PROD_DATABASE_URL", "")
        if not prod_url:
            # Try to get from Railway CLI
            try:
                import subprocess

                result = subprocess.run(
                    [
                        "railway",
                        "variables",
                        "--json",
                        "--service",
                        "Postgres",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    prod_url = data.get("DATABASE_PUBLIC_URL", "")
            except Exception:
                pass

        if not prod_url:
            raise ValueError(
                "Production database URL not found. Set PROD_DATABASE_URL or link Railway project."
            )
        return prod_url.replace("postgresql+asyncpg://", "postgresql://")

    raise ValueError(f"Unknown environment: {env}")


async def export_agent_data(conn: asyncpg.Connection, public_id: str) -> dict[str, Any]:
    """Export all data related to an agent."""
    agent = await conn.fetchrow("SELECT * FROM agents WHERE public_id = $1", public_id)
    if not agent:
        raise ValueError(f"Agent not found: {public_id}")

    agent_dict = dict(agent)

    # Get workspace association
    workspace_link = await conn.fetchrow(
        "SELECT * FROM agent_workspaces WHERE agent_id = $1", agent["id"]
    )

    workspace = None
    user_settings = None
    if workspace_link:
        workspace = await conn.fetchrow(
            "SELECT * FROM workspaces WHERE id = $1", workspace_link["workspace_id"]
        )
        user_settings = await conn.fetchrow(
            "SELECT * FROM user_settings WHERE workspace_id = $1",
            workspace_link["workspace_id"],
        )

    # Get user
    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", agent["user_id"])

    return {
        "version": "1.0",
        "exported_at": datetime.now(UTC).isoformat(),
        "agent": agent_dict,
        "workspace": dict(workspace) if workspace else None,
        "workspace_link": dict(workspace_link) if workspace_link else None,
        "user_settings": dict(user_settings) if user_settings else None,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "hashed_password": user["hashed_password"],
            "is_active": user["is_active"],
            "is_superuser": user["is_superuser"],
        }
        if user
        else None,
    }


async def import_agent_data(
    conn: asyncpg.Connection,
    data: dict[str, Any],
    skip_secrets: bool = False,
) -> None:
    """Import agent data to database."""
    # 1. Create/update user
    if user_data := data.get("user"):
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", user_data["email"]
        )
        if not existing_user:
            await conn.execute(
                """
                INSERT INTO users (id, email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                """,
                user_data["id"],
                user_data["email"],
                user_data["hashed_password"],
                user_data["full_name"],
                user_data["is_active"],
                user_data["is_superuser"],
            )
            print(f"✓ Created user: {user_data['email']}")
        else:
            print(f"✓ User exists: {user_data['email']}")

    # 2. Create/update workspace
    if ws_data := data.get("workspace"):
        existing_ws = await conn.fetchrow(
            "SELECT id FROM workspaces WHERE id = $1", UUID(ws_data["id"])
        )
        if not existing_ws:
            await conn.execute(
                """
                INSERT INTO workspaces (id, user_id, name, description, settings, is_default, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                """,
                UUID(ws_data["id"]),
                ws_data["user_id"],
                ws_data["name"],
                ws_data["description"],
                ws_data["settings"],
                ws_data["is_default"],
            )
            print(f"✓ Created workspace: {ws_data['name']}")
        else:
            print(f"✓ Workspace exists: {ws_data['name']}")

    # 3. Create/update agent
    agent_data = data["agent"]
    existing_agent = await conn.fetchrow(
        "SELECT id FROM agents WHERE public_id = $1", agent_data["public_id"]
    )
    if not existing_agent:
        await conn.execute(
            """
            INSERT INTO agents (
                id, user_id, name, description, pricing_tier, system_prompt, language, voice,
                turn_detection_mode, turn_detection_threshold, turn_detection_prefix_padding_ms,
                turn_detection_silence_duration_ms, temperature, max_tokens, initial_greeting,
                enabled_tools, enabled_tool_ids, phone_number_id, enable_recording, enable_transcript,
                provider_config, is_active, is_published, total_calls, total_duration_seconds,
                public_id, embed_enabled, allowed_domains, embed_settings, created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18,
                $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29, NOW(), NOW()
            )
            """,
            UUID(agent_data["id"]),
            agent_data["user_id"],
            agent_data["name"],
            agent_data["description"],
            agent_data["pricing_tier"],
            agent_data["system_prompt"],
            agent_data["language"],
            agent_data["voice"],
            agent_data["turn_detection_mode"],
            agent_data["turn_detection_threshold"],
            agent_data["turn_detection_prefix_padding_ms"],
            agent_data["turn_detection_silence_duration_ms"],
            agent_data["temperature"],
            agent_data["max_tokens"],
            agent_data["initial_greeting"],
            agent_data["enabled_tools"],
            agent_data["enabled_tool_ids"],
            agent_data["phone_number_id"],
            agent_data["enable_recording"],
            agent_data["enable_transcript"],
            agent_data["provider_config"],
            agent_data["is_active"],
            agent_data["is_published"],
            agent_data["total_calls"],
            agent_data["total_duration_seconds"],
            agent_data["public_id"],
            agent_data["embed_enabled"],
            agent_data["allowed_domains"],
            agent_data["embed_settings"],
        )
        print(f"✓ Created agent: {agent_data['name']} ({agent_data['public_id']})")
    else:
        print(f"✓ Agent exists: {agent_data['name']}")

    # 4. Create agent_workspace link
    if link_data := data.get("workspace_link"):
        existing_link = await conn.fetchrow(
            "SELECT agent_id FROM agent_workspaces WHERE agent_id = $1",
            UUID(link_data["agent_id"]),
        )
        if not existing_link:
            # Check schema for is_default column
            cols = await conn.fetch(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'agent_workspaces'"
            )
            col_names = [c["column_name"] for c in cols]

            if "is_default" in col_names:
                await conn.execute(
                    """
                    INSERT INTO agent_workspaces (id, agent_id, workspace_id, is_default, created_at, updated_at)
                    VALUES (gen_random_uuid(), $1, $2, $3, NOW(), NOW())
                    """,
                    UUID(link_data["agent_id"]),
                    UUID(link_data["workspace_id"]),
                    link_data.get("is_default", True),
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO agent_workspaces (agent_id, workspace_id, created_at)
                    VALUES ($1, $2, NOW())
                    """,
                    UUID(link_data["agent_id"]),
                    UUID(link_data["workspace_id"]),
                )
            print("✓ Created agent_workspace link")
        else:
            print("✓ Agent_workspace link exists")

    # 5. Create user_settings (with API keys if not skipping)
    if settings_data := data.get("user_settings"):
        existing_settings = await conn.fetchrow(
            "SELECT id FROM user_settings WHERE workspace_id = $1",
            UUID(settings_data["workspace_id"]),
        )
        if not existing_settings:
            if skip_secrets:
                # Create without API keys
                await conn.execute(
                    """
                    INSERT INTO user_settings (id, user_id, workspace_id, created_at, updated_at)
                    VALUES ($1, $2, $3, NOW(), NOW())
                    """,
                    UUID(settings_data["id"]),
                    UUID(settings_data["user_id"]),
                    UUID(settings_data["workspace_id"]),
                )
                print("✓ Created user_settings (without API keys - add manually)")
            else:
                await conn.execute(
                    """
                    INSERT INTO user_settings (
                        id, user_id, workspace_id, openai_api_key, deepgram_api_key, elevenlabs_api_key,
                        telnyx_api_key, telnyx_public_key, twilio_account_sid, twilio_auth_token,
                        created_at, updated_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
                    """,
                    UUID(settings_data["id"]),
                    UUID(settings_data["user_id"]),
                    UUID(settings_data["workspace_id"]),
                    settings_data.get("openai_api_key"),
                    settings_data.get("deepgram_api_key"),
                    settings_data.get("elevenlabs_api_key"),
                    settings_data.get("telnyx_api_key"),
                    settings_data.get("telnyx_public_key"),
                    settings_data.get("twilio_account_sid"),
                    settings_data.get("twilio_auth_token"),
                )
                print("✓ Created user_settings with API keys")
        else:
            print("✓ User_settings exists")


async def cmd_export(args: argparse.Namespace) -> None:
    """Export agent data to JSON file."""
    db_url = get_database_url(args.env)
    conn = await asyncpg.connect(db_url)

    try:
        data = await export_agent_data(conn, args.agent)

        # Optionally strip secrets
        if args.no_secrets and data.get("user_settings"):
            for key in list(data["user_settings"].keys()):
                if "key" in key.lower() or "token" in key.lower() or "password" in key.lower():
                    data["user_settings"][key] = None
            if data.get("user"):
                data["user"]["hashed_password"] = None

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, cls=UUIDEncoder)

        print(f"\n✅ Exported to {output_path}")

    finally:
        await conn.close()


async def cmd_import(args: argparse.Namespace) -> None:
    """Import agent data from JSON file."""
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Seed file not found: {input_path}")

    with open(input_path) as f:
        data = json.load(f)

    db_url = get_database_url(args.env)
    conn = await asyncpg.connect(db_url)

    try:
        await import_agent_data(conn, data, skip_secrets=args.no_secrets)
        print(f"\n✅ Imported to {args.env}")
    finally:
        await conn.close()


async def cmd_sync(args: argparse.Namespace) -> None:
    """Sync agent data between environments."""
    from_url = get_database_url(args.source)
    to_url = get_database_url(args.target)

    from_conn = await asyncpg.connect(from_url)
    to_conn = await asyncpg.connect(to_url)

    try:
        print(f"Syncing {args.agent} from {args.source} to {args.target}...")
        data = await export_agent_data(from_conn, args.agent)
        await import_agent_data(to_conn, data, skip_secrets=args.no_secrets)
        print(f"\n✅ Synced {args.agent} to {args.target}")
    finally:
        await from_conn.close()
        await to_conn.close()


async def cmd_list(args: argparse.Namespace) -> None:
    """List agents in an environment."""
    db_url = get_database_url(args.env)
    conn = await asyncpg.connect(db_url)

    try:
        agents = await conn.fetch(
            "SELECT public_id, name, is_active, embed_enabled FROM agents ORDER BY created_at"
        )
        print(f"\nAgents in {args.env}:")
        print("-" * 60)
        for a in agents:
            status = "✓" if a["is_active"] else "✗"
            embed = "📱" if a["embed_enabled"] else ""
            print(f"  {status} {a['public_id']}  {a['name']:<20} {embed}")
        print(f"\nTotal: {len(agents)} agents")
    finally:
        await conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ring Rookie Database Seed Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export agent data to JSON")
    export_parser.add_argument(
        "--env", default="local", choices=["local", "production"], help="Source environment"
    )
    export_parser.add_argument("--agent", required=True, help="Agent public_id to export")
    export_parser.add_argument("--output", "-o", required=True, help="Output JSON file path")
    export_parser.add_argument(
        "--no-secrets", action="store_true", help="Strip API keys and passwords"
    )

    # Import command
    import_parser = subparsers.add_parser("import", help="Import agent data from JSON")
    import_parser.add_argument(
        "--env", default="local", choices=["local", "production"], help="Target environment"
    )
    import_parser.add_argument("--input", "-i", required=True, help="Input JSON file path")
    import_parser.add_argument("--no-secrets", action="store_true", help="Skip importing API keys")

    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync agent between environments")
    sync_parser.add_argument("--source", default="local", help="Source environment")
    sync_parser.add_argument("--target", default="production", help="Target environment")
    sync_parser.add_argument("--agent", required=True, help="Agent public_id to sync")
    sync_parser.add_argument("--no-secrets", action="store_true", help="Skip syncing API keys")

    # List command
    list_parser = subparsers.add_parser("list", help="List agents in environment")
    list_parser.add_argument(
        "--env", default="local", choices=["local", "production"], help="Environment to list"
    )

    args = parser.parse_args()

    if args.command == "export":
        asyncio.run(cmd_export(args))
    elif args.command == "import":
        asyncio.run(cmd_import(args))
    elif args.command == "sync":
        asyncio.run(cmd_sync(args))
    elif args.command == "list":
        asyncio.run(cmd_list(args))


if __name__ == "__main__":
    main()
