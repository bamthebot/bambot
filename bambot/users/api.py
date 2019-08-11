import os
import requests


class User:
    def __init__(self, user_id, twitch_id, twitch_name, token):
        self.user_id = user_id
        self.twitch_id = twitch_id
        self.channel = twitch_name
        self.channel_token = token

    def __repr__(self):
        return self.channel

    def __str__(self):
        return self.channel

    def __eq__(self, other):
        return self.channel == other.channel

    def __hash__(self):
        return hash(f'{self.user_id}{self.channel}')


class UsersApi:
    endpoint = os.getenv('USERS_ENDPOINT')
    token = os.getenv('USERS_TOKEN')

    @staticmethod
    def get_users():
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {UsersApi.token}'
        }
        response = requests.get(UsersApi.endpoint, headers=headers).json()

        print(response)
        return {
            User(usr['user'], usr['twitch_id'], usr['twitch_name'], usr['access_token'])
            for usr in response
        }

    @staticmethod
    def refresh_user_token(user):
        pass
