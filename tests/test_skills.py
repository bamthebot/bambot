import pytest
from bambot.bangs.skills import TierOneSkillSet


@pytest.mark.asyncio
async def test_tierone_skill():
    tier_one = TierOneSkillSet()
    assert await tier_one.tierone() == "Tier One: " + ", ".join(tier_one.skills)


@pytest.mark.asyncio
async def test_leaderboard():
    tier_one = TierOneSkillSet()
    response = await tier_one.leaderboard("botw/Any%")
    assert "1)" in response and "2)" in response
