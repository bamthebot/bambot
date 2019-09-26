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


@pytest.mark.asyncio
async def test_worldrecord():
    tier_one = TierOneSkillSet()
    response = await tier_one.worldrecord("botw/Any%")
    assert "The WR for botw's Any% is" in response


@pytest.mark.asyncio
async def test_personalbests():
    tier_one = TierOneSkillSet()
    response = await tier_one.personalbests("Wolhaiksong")
    assert "Personal bests for Wolhaiksong are: " in response

    response = await tier_one.personalbest("Wolhaiksong/botw/Any%")
    assert "Personal bests for Wolhaiksong are: " in response
