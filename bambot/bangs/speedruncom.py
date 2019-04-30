import json
import requests


class SpeedrunComApiHelpers:

    @staticmethod
    def _get_ids(game, category, variable=False, value=False):
        game_url = 'https://www.speedrun.com/api/v1/games/{}'.format(game)
        game_req = requests.get(game_url)
        game_data = json.loads(game_req.text)['data']
        game_id = game_data['id']

        categories_uri, variables_uri =\
            [x['uri']
             for x in list(filter(lambda d: d['rel'] == 'variables' or d['rel'] == 'categories', game_data['links']))]

        categories_req = requests.get(str(categories_uri))
        categories_data = json.loads(categories_req.text)['data']
        category_data = list(filter(lambda d: category == d['name'], categories_data))[0]
        category_id = category_data['id']

        if variable:
            variables_req = requests.get(str(variables_uri))
            variables_data = json.loads(variables_req.text)['data']
            variable_data = list(filter(lambda d: variable == d['name'], variables_data))[0]
            variable_id = variable_data['id']
            if value:
                values_data = variable_data['values']['values']
                value_id = [k for k, v in values_data.items() if v['label'] == value][0]
                return game_id, category_id, variable_id, value_id
            return game_id, category_id, variable_id
        return game_id, category_id

    @staticmethod
    def get_top_str(game, category, variable=False, value=False):
        url = 'https://www.speedrun.com/api/v1/leaderboards'
        if value and variable:
            game_id, category_id, variable_id, value_id = SpeedrunComApiHelpers._get_ids(
                game, category, variable, value
            )
            leaderboard_url = '{}/{}/category/{}?var-{}={}'.format(url, game_id, category_id, variable_id, value_id)
        else:
            print(game, category)
            game_id, category_id = SpeedrunComApiHelpers._get_ids(game, category)
            print(game_id, category_id)
            # Fix for % in categories
            if '%' in category and category.strip('%').isdigit():
                category_id = category.strip('%')
            leaderboard_url = '{}/{}/category/{}'.format(url, game_id, category_id)

        req = requests.get(leaderboard_url)
        runs_data = json.loads(req.text)['data']['runs']
        runs = [run for run in runs_data if int(run['place']) <= 5]

        ret = ''
        for run in runs:
            run_place = int(run['place'])
            run_time = run['run']['times']['primary'][2:].lower()

            run_user_uri = run['run']['players'][0]['uri']
            req = requests.get(run_user_uri)
            user_name = json.loads(req.text)['data']['names']['international']
            ret += '{}) {}: {}  '.format(run_place, user_name, run_time)
        return ret
