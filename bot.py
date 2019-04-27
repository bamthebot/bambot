import os

from .bang_api import BangApi
from .twitch_irc_helpers import TwitchIrcConnection


class TwitchBot:
    nick = os.getenv('BOT_NICKNAME', 'bambot')
    token = os.getenv('BOT_TOKEN')
    bang_prefix = os.gentenv('COMMAND_PREFIX', '!')
    bang_api = BangApi()

    def __init__(self, channel, channel_token, user_id):
        self.channel = channel
        self.channel_token = channel_token
        self.irc_connection = TwitchIrcConnection(channel, self.nick, self.token)
        self.bangs = self.bang_api.get_bangs(user_id)

    def handle_connection(self):
        for message in self.irc_connection.get_messages():
            self.handle_message(message)

    def handle_message(self, message):
        if self.is_command(message):
            response = self.get_response(message)  # TODO
            self.send_command_response(response)  # TODO
        elif self.is_ping(message):  # TODO
            self.send_pong()  # TODO

    def is_command(self, message):
        if self.command_prefix == message[0]:
            return True
        return False
