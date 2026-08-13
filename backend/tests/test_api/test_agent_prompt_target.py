import pytest
from pydantic import ValidationError

from app.api.agents import CreateAgentRequest, UpdateAgentRequest

BASE_AGENT = {
    "name": "Test voice agent",
    "pricing_tier": "balanced",
    "system_prompt": "You are a helpful voice agent.",
    "language": "en",
    "enabled_tools": [],
    "enable_recording": False,
    "enable_transcript": True,
}


def test_prompt_character_target_defaults_to_5000() -> None:
    agent = CreateAgentRequest(**BASE_AGENT)

    assert agent.system_prompt_character_target == 5000


def test_prompt_character_target_accepts_saved_range() -> None:
    update = UpdateAgentRequest(system_prompt_character_target=7500)

    assert update.system_prompt_character_target == 7500


@pytest.mark.parametrize("value", [999, 20001])
def test_prompt_character_target_rejects_out_of_range(value: int) -> None:
    with pytest.raises(ValidationError):
        UpdateAgentRequest(system_prompt_character_target=value)
