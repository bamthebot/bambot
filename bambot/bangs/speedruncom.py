import aiohttp
import requests
from datetime import timedelta


http_client = aiohttp.ClientSession()


class SpeedrunAPIRequest:
    class SpeedrunAPIError(Exception):
        pass

    leaderboard_url = "https://www.speedrun.com/api/v1/leaderboards"
    games_url = "https://www.speedrun.com/api/v1/games/"
    pbs_base_url = "https://www.speedrun.com/api/v1/users/{}/personal-bests"
    embed_params = "?embed=categories.variables"

    def __init__(self, game, category, variable=None, variable_value=None):
        self.game = game.lower() if game is not None else None
        self.category = category
        self.variable = variable
        self.variable_value = variable_value

        self.game_data = None
        self.category_data = None
        self.variable_data = None

    def seconds_to_string(self, seconds):
        return str(timedelta(seconds=seconds)).strip("0").strip(":")

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
        if self.variable is None:
            return self
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

    def get_top_runs(self, number_of_runs=5):
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
                    "time": self.seconds_to_string(run["run"]["times"]["primary_t"])
                    .strip("0")
                    .strip(":"),
                }
            )
            i += 1
            if i >= number_of_runs:
                break
        return top_runs

    def get_top_str(self):
        try:
            runs = sorted(self.get_top_runs(5), key=lambda r: r["place"])
        except self.SpeedrunAPIError as speedrun_api_error:
            return str(speedrun_api_error)
        except Exception as e:
            print(e)
            return "An unexpected error occurred. Please contact the project mantainer."
        run_strings = [
            f'{run["place"]}) {run["player"]} [{run["time"]}]' for run in runs
        ]
        return " ".join(run_strings)

    def get_wr(self):
        try:
            run = self.get_top_runs(1)[0]
        except self.SpeedrunAPIError as speedrun_api_error:
            return str(speedrun_api_error)
        except Exception as e:
            print(e)
            return "An unexpected error occurred. Please contact the project mantainer."
        response = f'The WR for {self.game}\'s {self.category} is {run["time"]} by {run["player"]}.'
        if self.variable_value is not None:
            return response + f"[{self.variable_value}]"
        return response

    def build_personal_bests(self, runs):
        personal_bests = []
        runs = sorted(runs, key=lambda r: r["place"])
        for run in runs:
            place = run["place"]
            game_name = run["game"]["data"]["abbreviation"]
            category = run["category"]["data"]["name"]
            timing = self.seconds_to_string(run["run"]["times"]["primary_t"])
            variables = run["category"]["data"]["variables"]["data"]
            value_names = set()
            for variable_id, value_id in run["run"]["values"].items():
                value_names.update(
                    [
                        variable["values"]["values"][value_id]["label"]
                        for variable in variables
                        if variable["id"] == variable_id
                    ]
                )

            personal_bests.append(
                f"({place}) {game_name}/{category} [{', '.join(value_names)}][{timing}]"
            )  # noqa
        return personal_bests

    async def get_pbs(self, player, all_games=False):
        def suggestion_if_empty(runs, suggestion):
            if len(runs) == 0:
                raise self.SpeedrunAPIError(f"{suggestion}")

        pbs_url = self.pbs_base_url.format(player)
        params = {"embed": "category.variables,game"}
        async with http_client.get(pbs_url, params=params) as response:
            if response.status == 200:
                runs = await response.json()
                runs = runs["data"]
            else:
                raise self.SpeedrunAPIError(
                    "Couldn't get personal bests data. Please contact the project mantainer."
                )

        if all_games:
            personal_bests = self.build_personal_bests(runs)
            return f"Personal bests for {player} are: {', '.join(personal_bests)}"
        self._get_game_data()._get_category_data()
        self._get_ids()
        runs = [run for run in runs if run["run"]["game"] == self.game_id]
        possible_games = list({run["game"]["data"]["abbreviation"] for run in runs})
        suggestion_if_empty(
            runs,
            f"No runs were found for that game, please try again with: {','.join(possible_games)}",
        )

        runs = [run for run in runs if run["run"]["category"] == self.category_id]
        possible_categories = list({run["category"]["data"]["name"] for run in runs})
        suggestion_if_empty(
            runs,
            f"No runs were found for that game, please try again with: {','.join(possible_categories)}",
        )
        if self.variable is not None:
            self._get_variable_data()
            self._get_ids()
            runs = [run for run in runs if self.variable_id in run["run"]["values"]]
            suggestion_if_empty(
                runs,
                "No runs were found for that variable name, please try again with another name.",
            )
            runs = [
                run
                for run in runs
                if run["run"]["values"][self.variable_id] == self.variable_value_id
            ]
            suggestion_if_empty(
                runs,
                "No runs were found for that variable value, please try again with another value.",
            )
        personal_bests = self.build_personal_bests(runs)
        return f"Personal bests for {player} are: {', '.join(personal_bests)}"
