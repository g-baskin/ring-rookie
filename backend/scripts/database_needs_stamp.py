"""Exit successfully when a legacy schema needs an Alembic baseline stamp."""

import asyncio

from sqlalchemy import text

from app.db.session import engine


async def main() -> int:
    async with engine.connect() as connection:
        has_version_table = await connection.scalar(
            text("SELECT to_regclass('public.alembic_version')")
        )
        has_users = await connection.scalar(text("SELECT to_regclass('public.users')"))
        version_count = 0
        if has_version_table:
            version_count = await connection.scalar(text("SELECT count(*) FROM alembic_version"))

    return 0 if has_users and version_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
