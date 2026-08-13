"""Prepare PostgreSQL extensions before Alembic applies the schema."""

import asyncio

from sqlalchemy import text

from app.db.session import engine


async def main() -> None:
    async with engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


if __name__ == "__main__":
    asyncio.run(main())
