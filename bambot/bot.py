import asyncio
import os
import websockets

from datetime import datetime, timedelta

from .bangs.common import BangSet
from .bangs.common import SpecialBangSet
from .bangs.skills import SkillSet
from .irc.twitch_irc import TwitchIrcConnection


class TwitchBot:
    class ControlSkillSet(SkillSet):
        def __init__(self, user_id, controls):
            self.user_id = user_id
            for control in controls:
                setattr(self, control.__name__, control)
            self._get_skills()

    nick = os.getenv("BOT_NICKNAME", "bamthebot")
    token = os.getenv("BOT_TOKEN")
    not_found_response = os.getenv(
        "NOT_FOUND_RESPONSE", "Command not found. Try with !list, !wr or !help"
    )

    def __init__(self, user):
        self.user = user
        self.channel = user.channel
        self.channel_token = user.channel_token
        self.user_id = user.user_id
        self.bang_prefix = user.bang_prefix
        self.irc_connection = TwitchIrcConnection(self.channel, self.nick, self.token)
        self.user_bang_set = BangSet(self.user_id)
        self.last_updated = datetime.now()
        self.user_special_bang_set = SpecialBangSet(self.user_id)
        self.control_bang_set = SpecialBangSet(
            self.user_id,
            skill_set=self.ControlSkillSet(self.user_id, [self.mute, self.help, self.list]),
        )
        self.muted = False
        self.just_muted = False
        self.connecting = False

    async def handle_connection(self):
        self.connecting = True
        if self.irc_connection.websocket is None:
            print("Websocket not instantiated. Creating websocket.")
            await self.irc_connection.connect()
        while self.irc_connection.websocket.open:
            print(f"Handling {self.channel}'s connection.")
            try:
                async for message in self.irc_connection:
                    await self.handle_message(message)
            except websockets.exceptions.ConnectionClosed:
                print("Websocket connection closed. Reconnecting websocket.")
                await self.irc_connection.connect()

    async def update_bangs(self):
        print("Updating Bangs!")
        self.user_bang_set.update()
        self.last_updated = datetime.now()

    async def handle_message(self, message):
        message = self.user.replace_with_blasts(message)
        if self.is_bang(message):
            response = await self.get_response(message)
            if not self.muted or self.just_muted:
                self.just_muted = False
                await self.irc_connection.send_channel_message(response)
        elif self.irc_connection.is_ping(message):
            await self.irc_connection.send_pong()

    def is_bang(self, message):
        if len(message) == 0:
            return False
        if self.bang_prefix == message[0]:
            return True
        return False

    async def get_response(self, message):
        if self.last_updated < datetime.now() - timedelta(minutes=3):
            self.update_bangs()
        print("Getting response for", message)
        message = message.strip().strip(self.bang_prefix).split(" ")
        command = message[0]
        print("Command is", command, command in self.user_bang_set)
        command_args = None
        if len(message) > 1:
            command_args = message[1:]
        response = None

        if command in self.control_bang_set:
            response = await self.control_bang_set.process_command(command, command_args)
        elif command in self.user_special_bang_set:
            print("Command is special")
            response = await self.user_special_bang_set.process_command(command, command_args)
        elif command in self.user_bang_set:
            print("Command is normal")
            response = self.user_bang_set[command]
        else:
            response = self.not_found_response

        response = self.user.replace_with_blasts(response)
        if self.is_bang(response):
            return await self.get_response(response)
        return response

    def get_commands(self):
        return (
            list(self.user_special_bang_set)
            + list(self.user_bang_set)
            + list(self.control_bang_set)
        )

    async def close_connection(self):
        await self.irc_connection.disconnect()

    # Control Skills
    async def mute(self, *args, **kwargs):
        """Makes the bot shut up"""
        self.muted = not self.muted  # toogle
        if self.muted:
            self.just_muted = True
            return "I've been muted :("
        return "I'm back! :D"

    async def help(self, *args, **kwargs):
        """Displays the help text for a special command"""
        if len(args) == 0:
            return self.help.__doc__
        docs = []
        for command in args:
            if command in self.user_special_bang_set:
                docs.append(self.user_special_bang_set[command].bang_skill.__doc__)
            elif command in self.control_bang_set:
                docs.append(self.control_bang_set[command].bang_skill.__doc__)

        return "| ".join(docs)

    async def list(self, *args, **kwargs):
        """List all commands available."""
        return f"Command list: {', '.join(self.get_commands())}"
