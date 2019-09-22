from bambot.bangs.skills import TierOneSkillSet


def test_tierone_skill():
    tier_one = TierOneSkillSet()
    assert tier_one.tierone() == "Tier One: " + ", ".join(tier_one.skills)


def test_leaderboard():
    tier_one = TierOneSkillSet()
    response = tier_one.leaderboard("botw/Any%")
    assert "1)" in response and "2)" in response
