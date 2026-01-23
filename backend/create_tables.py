"""Create all database tables from models."""
import asyncio
from app.db.session import engine
from app.db.base import Base
# Import all models to ensure they're registered
from app.models.user import User  # noqa: F401
from app.models.agent import Agent  # noqa: F401
from app.models.contact import Contact  # noqa: F401
from app.models.appointment import Appointment  # noqa: F401
from app.models.call_interaction import CallInteraction  # noqa: F401
from app.models.workspace import Workspace, AgentWorkspace  # noqa: F401
from app.models.call_record import CallRecord  # noqa: F401
from app.models.user_settings import UserSettings  # noqa: F401
from app.models.user_integration import UserIntegration  # noqa: F401
from app.models.phone_number import PhoneNumber  # noqa: F401


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_all())
