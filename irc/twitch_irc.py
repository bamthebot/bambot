import logging
import os

from websockets import client

logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())


class TwitchIrcConnection:
    uri = os.getenv('TWITCH_URI')

    def __init__(self, channel, nick, token):
        self.channel = channel
        self.nick = nick
        self.token = token
        self.websocket = None

    async def connect(self):
        self.websocket = await client.connect(self.uri)
        self.websocket.send(f'PASS oauth:{self.token}')
        self.websocket.send(f'NICK {self.nick}')
        self.websocket.send(f'JOIN #{self.channel}')

    async def send_channel_message(self, message):
        await self.websocket.send(f'PRIVMSG #{self.channel.lower()} :{message}')

    async def send_pong(self):
        await self.websocket.send('PONG :tmi.twitch.tv')

    def is_ping(message):
        if message == 'PING :tmi.twitch.tv':
            return True

    def __aiter__(self):
        return self

    async def __anext_(self):
        message = await self.websocket
        channel_message = message.split(':')
        if len(channel_message) < 2:
            return ''
        channel_message = ':'.join(channel_message[2:])
        return channel_message
