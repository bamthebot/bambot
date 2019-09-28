import asyncio
import logging
import os

from websockets import client

logger = logging.getLogger('websockets.server')
logger.setLevel(logging.ERROR)
logger.addHandler(logging.StreamHandler())


class TwitchIrcConnection:
    MAX_MESSAGES_CHARCOUNT = 500
    uri = os.getenv('TWITCH_URI')

    def __init__(self, channel, nick, token):
        self.channel = channel.strip()
        self.nick = nick.strip()
        self.token = token.strip()
        self.websocket = None
        self.message_split_character = " "

    async def connect(self):
        if self.websocket is not None:
            self.websocket.close()
        print(f'Connecting to TwtichIRC ({self.uri})')
        self.websocket = await client.connect(self.uri)
        print(f'Authenticating and entering {self.channel}')
        print(f'PASS {self.token}')
        print(f'NICK {self.nick}')
        print(f'JOIN #{self.channel}')

        await self.websocket.send(f'PASS {self.token}')
        await self.websocket.send(f'NICK {self.nick}')
        await self.websocket.send(f'JOIN #{self.channel}')

    def split_channel_message(self, message):
        breakpoint()
        messages = []
        while len(message) > self.MAX_MESSAGES_CHARCOUNT:
            split_message = message[:self.MAX_MESSAGES_CHARCOUNT]
            last_split_character = split_message.rfind(self.message_split_character)
            partial_message, message = message[:last_split_character], message[last_split_character:]
            messages.append(partial_message)
        messages.append(message)
        return messages

    async def send_channel_message(self, message):
        if len(message) > self.MAX_MESSAGES_CHARCOUNT:
            messages = self.split_channel_message(message)
        else:
            messages = [message]
        for message in messages:
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
