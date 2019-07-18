import os
import requests

from . import skills


class BangsApi:
    endpoint = os.getenv('BANGS_ENDPOINT')
    token = os.getenv('BANGS_TOKEN')
    response = None

    def __init__(self):
        if self.response is None:
            self.get_response()

    def get_response(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {self.token}'
        }
        print(headers)
        self.response = requests.get(self.endpoint, headers=headers).json()

    def get_user_bangs(self, user_id, update=False):
        if update:
            self.get_response()
        print(f'Getting bangs for user-id {user_id}')
        bangs = [
            Bang(usrbng['command'], usrbng['response'])
            for usrbng in self.response
        ]
        print(f'Bangs: {[bang.command for bang in bangs]}')
        return bangs


class Bang:
    def __init__(self, command, response):
        self.command = command
        self.response = response


class BangSet:
    class BangNotFound(Exception):
        pass

    def __init__(self, user_id):
        self.user_id = user_id
        self.bangs_api = BangsApi()
        self.update()

    def update(self):
        self.bangs = self.bangs_api.get_user_bangs(self.user_id, update=True)
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


class SpecialBang:
    def __init__(self, command, bang_skill):
        self.command = command
        self.response = SpecialResponse(bang_skill)


class SpecialResponse:
    def __init__(self, bang_skill):
        self.bang_skill = bang_skill

    def process_args(self, *args):
        return self.bang_skill(*args)


class SpecialBangSet(BangSet):

    def __init__(self, user_id):
        self.user_id = user_id
        self.tier_one = skills.TierOneSkillSet()
        self.update()

    def update(self):
        self.bangs = [
            SpecialBang(skill, getattr(self.tier_one, skill))
            for skill in self.tier_one
        ]
        self.bang_commands = [bang.command for bang in self.bangs]
