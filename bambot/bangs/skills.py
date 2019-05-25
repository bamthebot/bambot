from .speedruncom import SpeedrunComApiHelpers


class SkillSet:
    tier = None

    def __init__(self):
        self._get_skills()

    def __iter__(self):
        return iter(self.skills)

    def _get_skills(self):
        self.skills = [
            func for func in dir(self)
            if callable(getattr(self, func))
            and not func.startswith("_")
        ]


class TierOneSkillSet(SkillSet):
    tier = 1

    def tierone(self, *args):
        """Bang that returns current tier one special bangs."""
        if self.skills is None:
            self._get_skills()
        return 'Tier One: ' + ', '.join(self.skills)

    def tierone_help(self, *args):
        """Bang that returns a description for a given command name.

        Args:
            a string containing a bang name.
        Usage:
            "!tierone_help tierone"
            "!tierone_help tierone_help"
        """
        if len(args) == 0:
            return self.tierone_help.__doc__

        skill = args[0]
        if skill in self.skills:
            return getattr(self, skill).__doc__
        else:
            return self.tierone_help.__doc__

    def leaderboard(self, *args):
        """Bang that consumes the speedrun.com api to fetch a game's
        top speedruns data.

        Args:
            a string containing slash separated values in the following order.
            game/category/variable/variable-value
        Usage:
            "!leaderboard <game>/<category>[/variable/variable_value]"
        Examples:
            "!leaderborad botw/Any%"
            "!leaderborad botw/Any%/Amiibo/No Amiboo"
        """
        if len(args) == 0:
            return self.leaderboard.__doc__
        args = args[0].strip().split('/')
        print(args)
        try:
            return SpeedrunComApiHelpers.get_top_str(*args)
        except IndexError:
            return 'Speedrun search failed. Try adapting your parameters.'
