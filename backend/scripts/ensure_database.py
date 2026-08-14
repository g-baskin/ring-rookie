"""Create the configured PostgreSQL database when a persisted cluster predates it."""

import asyncio
import re

import asyncpg
from sqlalchemy.engine import make_url

from app.core.config import settings


async def main() -> None:
    database_url = make_url(str(settings.DATABASE_URL))
    database_name = database_url.database
    if database_name is None or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", database_name) is None:
        raise ValueError("DATABASE_URL must contain a safe PostgreSQL database name")

    connection = await asyncpg.connect(
        host=database_url.host,
        port=database_url.port or 5432,
        user=database_url.username,
        password=database_url.password,
        database="postgres",
    )
    try:
        exists = await connection.fetchval(
            "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)",
            database_name,
        )
        if not exists:
            await connection.execute(f'CREATE DATABASE "{database_name}"')
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
