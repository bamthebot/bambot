from .speedruncom import SpeedrunAPIRequest


class SkillSet:
    tier = None

    def __init__(self):
        self._get_skills()

    def __iter__(self):
        return iter(self.skills)

    def _get_skills(self):
        self.skills = [
            func
            for func in dir(self)
            if callable(getattr(self, func)) and not func.startswith("_")
        ]


class TierOneSkillSet(SkillSet):
    tier = 1

    def tierone(self, *args):
        """Bang that returns current tier one special bangs."""
        if self.skills is None:
            self._get_skills()
        return "Tier One: " + ", ".join(self.skills)

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
            "!leaderboard botw/Any%"
            "!leaderboard botw/Any%/Amiibo/No Amiboo"
        """
        if len(args) == 0:
            return self.leaderboard.__doc__
        args = args[0].strip().split("/")
        print(args)
        return SpeedrunAPIRequest(*args).get_top_str()

    def worldrecord(self, *args):
        """Bang that consumes the speedrun.com api to fetch a game's
        world record data.

        Args:
            a string containing slash separated values in the following order.
            game/category/variable/variable-value
        Usage:
            "!worldrecord <game>/<category>[/variable/variable_value]"
        Examples:
            "!worldrecord botw/Any%"
            "!worldrecord botw/Any%/Amiibo/No Amiboo"
        """

        if len(args) == 0:
            return self.worldrecord.__doc__
        args = args[0].strip().split("/")
        return SpeedrunAPIRequest(*args).get_wr()

    def personalbest(self, *args):
        """Bang that gets the PB from a player on a given game.

        Args:
            a string containing slash separated values in the following order.
            player/game/category/variable/variable-value
        Usage:
            "!personalbest player/<game>/<category>[/variable/variable_value]"
        Examples:
            "!personalbest bambot/botw/Any%"
            "!personalbest bambot/botw/Any%/Amiibo/No Amiboo"
        """
        if len(args) == 0:
            return self.personalbest.__doc__
        player, *args = args[0].strip().split("/")
        return SpeedrunAPIRequest(*args).get_pbs(player, all_games=False)

    def personalbests(self, *args):
        """Bang that gets the PBs from a player on all of his games.

        Args:
            a player name
        Usage:
            "!personalbests <player>"
        Examples:
            "!personalbests bambot"
        """
        if len(args) == 0:
            return self.personalbest.__doc__
        player, *args = args[0].strip().split("/")
        return SpeedrunAPIRequest(None, None).get_pbs(player, all_games=True)
