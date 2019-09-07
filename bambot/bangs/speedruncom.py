import requests
from datetime import timedelta


class SpeedrunAPIRequest:
    class SpeedrunAPIError(Exception):
        pass

    leaderboard_url = "https://www.speedrun.com/api/v1/leaderboards"
    games_url = "https://www.speedrun.com/api/v1/games/"
    embed_params = "?embed=categories.variables"

    def __init__(self, game, category, variable=None, variable_value=None):
        self.game = game
        self.category = category
        self.variable = variable
        self.variable_value = variable_value

        self.game_data = None
        self.category_data = None
        self.variable_data = None

    def _get_data_by_name(self, name, data):
        return [d for d in data if d["name"] == name]

    def _get_names_from_data(self, data):
        return [d["name"] for d in data]

    def _get_game_data(self):
        url = self.games_url + self.game + self.embed_params
        print(url)
        response = requests.get(url)
        if response.ok:
            self.game_data = response.json()["data"]
            return self
        raise self.SpeedrunAPIError(
            "Game not found, please check again with the speedrun.com values."
        )

    def _get_category_data(self):
        categories = self.game_data["categories"]["data"]
        category_data = self._get_data_by_name(self.category, categories)
        if not len(category_data):
            category_names = "[{}]".format(
                "], [".join(self._get_names_from_data(categories))
            )
            raise self.SpeedrunAPIError(
                f"Category not found. Please try with any of the following category names: {category_names}"
            )
        self.category_data = category_data[0]
        return self

    def _get_variable_data(self):
        variables = self.category_data["variables"]["data"]
        variable_data = self._get_data_by_name(self.variable, variables)
        if not len(variable_data):
            variable_names = "[{}]".format(
                "], [".join(self._get_names_from_data(variables))
            )
            raise self.SpeedrunAPIError(
                f"Variable not found. Please try with any of the following variable names: {variable_names}"
            )
        self.variable_data = variable_data[0]
        return self

    def _get_variable_value_id(self):
        variable_values = self.variable_data["values"]["values"]
        value_data = [
            k for k, v in variable_values.items() if v["label"] == self.variable_value
        ]
        if not len(value_data):
            variable_value_names = "[{}]".format(
                "], [".join([v["label"] for v in variable_values.values()])
            )
            raise self.SpeedrunAPIError(
                f"Variable value not found. Please try with any of the following variable value names: {variable_value_names}"  # noqa
            )
        self.variable_value_id = value_data[0]
        return self

    def _get_ids(self):
        self.game_id = self.game_data["id"]
        self.category_id = self.category_data["id"]
        if self.variable_data is not None:
            self.variable_id = self.variable_data["id"]
            self._get_variable_value_id()
        return self

    def _get_leaderboard_data(self):
        self._get_game_data()._get_category_data()
        if self.variable is not None:
            self._get_variable_data()
        self._get_ids()
        url = f"{self.leaderboard_url}/{self.game_id}/category/{self.category_id}?embed=players"
        if self.variable is not None:
            url += f"&var-{self.variable_id}={self.variable_value_id}"
        response = requests.get(url)
        if response.ok:
            self.leaderboard_data = response.json()["data"]
            return self
        raise self.SpeedrunAPIError(
            "Couldn't fetch leaderboard data. Please contact the project mantainer."
        )

    def _get_player_name(self, id_):
        for player in self.leaderboard_data["players"]["data"]:
            if "id" in player and player["id"] == id_:
                return player["names"]["international"]

    def get_top_runs(self):
        self._get_leaderboard_data()
        top_runs = []
        i = 0
        for run in self.leaderboard_data["runs"]:
            players = run["run"]["players"]

            player_names = [
                p["name"] if p["rel"] == "guest" else self._get_player_name(p["id"])
                for p in players
            ]
            player_name = " and ".join(player_names)
            top_runs.append(
                {
                    "place": run["place"],
                    "player": player_name,
                    "time": str(timedelta(seconds=run["run"]["times"]["primary_t"]))
                    .strip("0")
                    .strip(":"),
                }
            )
            i += 1
            if i >= 5:
                break
        return top_runs

    def get_top_str(self):
        try:
            runs = sorted(self.get_top_runs(), key=lambda r: r["place"])
        except self.SpeedrunAPIError as speedrun_api_error:
            return str(speedrun_api_error)
        except Exception as e:
            print(e)
            return "An unexpected error occurred. Please contact the project mantainer."
        run_strings = [
            f'{run["place"]}) {run["player"]} [{run["time"]}]' for run in runs
        ]
        return " ".join(run_strings)
