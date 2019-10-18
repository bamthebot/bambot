import os
import requests


class User:
    def __init__(self, user_id, twitch_id, twitch_name, token, bang_prefix, blasts=[]):
        self.user_id = user_id
        self.twitch_id = twitch_id
        self.channel = twitch_name.lower()
        self.channel_token = token
        self.bang_prefix = bang_prefix
        self.blasts = blasts

    def __repr__(self):
        return self.channel

    def __str__(self):
        return self.channel

    def __eq__(self, other):
        return self.channel == other.channel

    def __hash__(self):
        return hash(f"{self.user_id}{self.channel}")

    def replace_with_blasts(self, base):
        for blast in self.blasts:
            replace_template = f"$({blast['name']})"
            base = base.replace(replace_template, blast["value"])
        return base


class UsersApi:
    endpoint = os.getenv("USERS_ENDPOINT")
    token = os.getenv("USERS_TOKEN")
    user_override = os.getenv("USER_OVERRIDE", None)

    @staticmethod
    def get_users():
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {UsersApi.token}",
        }
        response = requests.get(UsersApi.endpoint, headers=headers).json()

        print(response)
        if UsersApi.user_override is not None:
            response = [
                user
                for user in response
                if user["twitch_name"] == UsersApi.user_override
            ]
            print(response)
        return {
            User(
                usr["user"],
                usr["twitch_id"],
                usr["twitch_name"],
                usr["access_token"],
                usr["command_character"],
                usr["blasts"],
            )
            for usr in response
        }

    @staticmethod
    def refresh_user_token(user):
        pass
