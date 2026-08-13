"""Focused tests for live Telnyx phone-number synchronization."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.telephony import list_phone_numbers
from app.core.auth import user_id_to_uuid
from app.models.user import User
from app.services.telephony.base import PhoneNumber
from app.services.telephony.telnyx_service import TelnyxService


@pytest.mark.asyncio
async def test_telnyx_sync_uses_account_credentials_for_all_workspaces() -> None:
    """Omitting workspace_id must use account-level Telnyx credentials."""
    user = User(
        id=7,
        email="owner@example.com",
        hashed_password="unused",  # noqa: S106 -- inert value; auth is not exercised
    )
    db = AsyncMock(spec=AsyncSession)
    account_settings = SimpleNamespace(
        telnyx_api_key="account-api-key",
        telnyx_public_key="account-public-key",
    )
    telnyx_numbers = [
        PhoneNumber(
            id="number-1",
            phone_number="+15551234567",
            friendly_name="Ring Rookie Voice Connection",
            provider="telnyx",
            capabilities={"voice": True, "sms": True},
        )
    ]

    with (
        patch(
            "app.api.telephony.get_user_api_keys",
            new=AsyncMock(return_value=account_settings),
        ) as get_api_keys,
        patch("app.api.telephony.TelnyxService") as telnyx_service_class,
    ):
        telnyx_service_class.return_value.list_phone_numbers = AsyncMock(
            return_value=telnyx_numbers
        )
        result = await list_phone_numbers(
            current_user=user,
            db=db,
            provider="telnyx",
            workspace_id=None,
        )

    get_api_keys.assert_awaited_once_with(user_id_to_uuid(user.id), db, workspace_id=None)
    telnyx_service_class.assert_called_once_with(
        api_key="account-api-key",
        public_key="account-public-key",
    )
    assert [number.model_dump() for number in result] == [
        {
            "id": "number-1",
            "phone_number": "+15551234567",
            "friendly_name": "Ring Rookie Voice Connection",
            "provider": "telnyx",
            "capabilities": {"voice": True, "sms": True},
            "assigned_agent_id": None,
        }
    ]


@pytest.mark.asyncio
async def test_telnyx_sync_uses_selected_workspace_credentials() -> None:
    """A selected workspace must use only that workspace's Telnyx credentials."""
    user = User(
        id=8,
        email="member@example.com",
        hashed_password="unused",  # noqa: S106 -- inert value; auth is not exercised
    )
    db = AsyncMock(spec=AsyncSession)
    workspace_id = uuid.uuid4()
    workspace_settings = SimpleNamespace(
        telnyx_api_key="workspace-api-key",
        telnyx_public_key="workspace-public-key",
    )

    with (
        patch(
            "app.api.telephony.get_user_api_keys",
            new=AsyncMock(return_value=workspace_settings),
        ) as get_api_keys,
        patch("app.api.telephony.TelnyxService") as telnyx_service_class,
    ):
        telnyx_service_class.return_value.list_phone_numbers = AsyncMock(return_value=[])
        result = await list_phone_numbers(
            current_user=user,
            db=db,
            provider="telnyx",
            workspace_id=str(workspace_id),
        )

    assert result == []
    get_api_keys.assert_awaited_once_with(user_id_to_uuid(user.id), db, workspace_id=workspace_id)
    telnyx_service_class.assert_called_once_with(
        api_key="workspace-api-key",
        public_key="workspace-public-key",
    )


@pytest.mark.asyncio
async def test_telnyx_sync_maps_number_connection_and_capability_fields() -> None:
    """Telnyx response fields must survive conversion to the dashboard contract."""
    service = TelnyxService(api_key="test-api-key")
    response = MagicMock()
    response.json.return_value = {
        "data": [
            {
                "id": "number-2",
                "phone_number": "+15557654321",
                "connection_name": "Support SIP Connection",
                "messaging_profile_id": "profile-1",
            }
        ]
    }
    client = AsyncMock()
    client.get.return_value = response

    with patch.object(service, "_get_http_client", new=AsyncMock(return_value=client)):
        result = await service.list_phone_numbers()

    client.get.assert_awaited_once_with("/phone_numbers")
    assert result == [
        PhoneNumber(
            id="number-2",
            phone_number="+15557654321",
            friendly_name="Support SIP Connection",
            provider="telnyx",
            capabilities={"voice": True, "sms": True},
        )
    ]
