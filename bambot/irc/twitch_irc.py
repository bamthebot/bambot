import asyncio
import logging
import os

from websockets import client

logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())


class TwitchIrcConnection:
    uri = os.getenv('TWITCH_URI')

    def __init__(self, channel, nick, token):
        self.channel = channel.strip()
        self.nick = nick.strip()
        self.token = token.strip()
        self.websocket = None

    async def connect(self):
        print(f'Connecting to TwtichIRC ({self.uri})')
        self.websocket = await client.connect(self.uri)
        print(f'Authenticating and entering {self.channel}')
        await self.websocket.send(f'PASS {self.token}')
        print(f'PASS {self.token}')
        await asyncio.sleep(3)
        await self.websocket.send(f'NICK {self.nick}')
        print(f'NICK {self.nick}')
        await asyncio.sleep(3)
        await self.websocket.send(f'JOIN #{self.channel}')
        await asyncio.sleep(3)
        print(f'JOIN #{self.channel}')

    async def send_channel_message(self, message):
        print(f'SENDING: {message}')
        await self.websocket.send(f'PRIVMSG #{self.channel.lower()} :{message}')

    async def send_pong(self):
        print('PONGED')
        await self.websocket.send('PONG :tmi.twitch.tv')

    def is_ping(self, message):
        if message == 'PING :tmi.twitch.tv':
            return True

    async def __aiter__(self):
        async for message in self.websocket:
            print(message)
            channel_message = message.split(':')
            if len(channel_message) < 2:
                yield ''
            channel_message = ':'.join(channel_message[2:])
            yield channel_message

    async def disconnect(self):
        await self.websocket.send(f'PART #{self.channel}')
        await self.websocket.close()
