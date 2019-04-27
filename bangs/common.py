import os
import requests


class SpecialResponse:
    def __init__(self, bang_ability, empty_response):
        self.bang_ability = bang_ability

    def process_args(self, args):
        args = args.split()
        return self.bang_ability(*args)


class Bang:
    def __init__(self, command, response):
        self.command = command
        self.response = response


class SpecialBang(Bang):
    def __init__(self, command, response, bang_ability, empty_response):
        super(Bang, self).__init__(command, response)
        self.response = SpecialResponse(bang_ability, empty_response)
        self.empty_response = empty_response


class BangsApi:
    endpoint = os.getenv('BANGS_ENDPOINT')
    token = os.getenv('BANGS_TOKEN')
    response = None

    def __init__(self):
        if self.response is None:
            self.get_response()

    def get_response(self):
        headers = {
            'Content-Type': 'application/json'
        }
        self.response = requests.get(self.endpoint, headers=headers).json()

    def get_user_bangs(self, user_id):
        return [
            Bang(usrbng['command'], usrbng['response'])
            for usrbng in self.response
        ]


class BangSet:
    class BangNotFound(Exception):
        pass

    def __init__(self, user_id):
        self.user_id = user_id
        self.bangs_api = BangsApi()
        self.bangs = self.bangs_api.get_user_bangs(self.user_id)
        self.bang_commands = [bang.command for bang in self.bangs]

    def __iter__(self):
        return iter(self.bang_commands)

    def __contains__(self, item):
        return item in self.bang_commands

    def keys(self):
        return self.bang_commands

    def __getitem__(self, item):
        try:
            return next(b.response for b in self.bangs if b.command == item)
        except StopIteration:
            raise BangSet.BangNotFound('{} has no {} bang.'.format(self.user_id, item))


class SpecialBangSet(BangSet):  # TODO

    def __iter__(self):
        return iter([])

    def __contains__(self):
        return False

    def keys(self):
        return []

    def __getitem__(self, item):
        raise BangSet.BangNotFound('{} has no {} bang.'.format(self.user_id, item))
