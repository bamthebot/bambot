import os
import websockets

from .bangs.common import BangSet
from .bangs.common import SpecialBangSet
from .irc.twitch_irc import TwitchIrcConnection


class TwitchBot:
    nick = os.getenv('BOT_NICKNAME', 'bamthebot')
    token = os.getenv('BOT_TOKEN')
    bang_prefix = os.getenv('COMMAND_PREFIX', '!')
    not_found_response = os.getenv('NOT_FOUND_RESPONSE', 'Bang not found, please try with: ')

    def __init__(self, user):
        self.user = user
        self.channel = user.channel
        self.channel_token = user.channel_token
        self.user_id = user.user_id
        self.irc_connection = TwitchIrcConnection(self.channel, self.nick, self.token)
        self.user_bang_set = BangSet(self.user_id)
        self.user_special_bang_set = SpecialBangSet(self.user_id)
        self.connecting = False

    async def handle_connection(self):
        self.connecting = True
        if self.irc_connection.websocket is None:
            print('Websocket not instantiated. Creating websocket.')
            await self.irc_connection.connect()
        while self.irc_connection.websocket.open:
            print(f'Handling {self.channel}\'s connection.')
            try:
                async for message in self.irc_connection:
                    await self.handle_message(message)
            except websockets.exceptions.ConnectionClosed:
                await self.irc_connection.connect()

    async def handle_message(self, message):
        if self.is_bang(message):
            response = self.get_response(message)
            await self.irc_connection.send_channel_message(response)
        elif self.irc_connection.is_ping(message):
            await self.irc_connection.send_pong()

    def is_bang(self, message):
        if len(message) == 0:
            return False
        if self.bang_prefix == message[0]:
            return True
        return False

    def get_response(self, message):
        print('Updating Bangs!')
        self.user_bang_set.update()
        print('Getting response for', message)
        message = message.strip().strip(self.bang_prefix).split(' ')
        command = message[0]
        print('Command is', command, command in self.user_bang_set)
        command_args = None
        if len(message) > 1:
            command_args = message[1:]
        response = None

        if command in self.user_special_bang_set:
            print('Command is special')
            response = self.user_special_bang_set[command]
            if command_args is not None:
                args = ' '.join(command_args)
                response = response.process_args(args)
            else:
                response = response.process_args()
        elif command in self.user_bang_set:
            print('Command is normal')
            response = self.user_bang_set[command]
        else:
            response = self.not_found_response + ', '.join(self.get_commands())

        if self.is_bang(response):
            return self.get_response(response)

        return response

    def get_commands(self):
        return list(self.user_special_bang_set) + list(self.user_bang_set)

    async def close_connection(self):
        await self.irc_connection.disconnect()
