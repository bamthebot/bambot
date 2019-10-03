import asyncio
import os

from .bot import TwitchBot
from .users.api import UsersApi


class TwitchBotMaster:
    update_time = os.getenv('BOTS_UPDATE_TIME', 30)

    def __init__(self):
        self.users = set()
        self.bots = []

    async def update_bots(self, once=False):
        while self.continue_running():
            print('Updating Bots')
            old_users = self.users
            self.users = UsersApi.get_users()
            new_users = self.users - old_users
            deleted_users = old_users - self.users
            print('Old:', old_users)
            print('New:', new_users)
            print('Deleted:', deleted_users)

            self.bots.extend([TwitchBot(user) for user in new_users])

            for user in deleted_users:
                bot = [tb for tb in self.bots if tb.user == user][0]
                await bot.close_connection()
            self.bots = [tb for tb in self.bots if tb.user not in deleted_users]
            for bot in self.bots:
                await bot.update_bangs()
                try:
                    user = next(user for user in self.users if user == bot.user)
                    bot.bang_prefix = user.bang_prefix
                except StopIteration:
                    continue
            if once:
                break
            await asyncio.sleep(self.update_time)

    async def check_bots(self):
        TwitchBot.token = [user.channel_token for user in self.users if user.channel == TwitchBot.nick][0]
        while self.continue_running():
            print('Checking Bots')
            for bot in self.bots:
                if bot.irc_connection.websocket is None:
                    continue
                if bot.irc_connection.websocket.closed:
                    user = bot.user
                    self.bots = [tb for tb in self.bots if tb.user != user]
                    self.bots.append(TwitchBot(user))
            await asyncio.sleep(10)

    async def handle_bots(self):
        while self.continue_running():
            print('Handling Bots')
            for bot in self.bots:
                if not bot.connecting:
                    asyncio.create_task(bot.handle_connection())
            await asyncio.sleep(10)

    async def display_info(self):
        channels = [bot.user.channel for bot in self.bots]
        print('Current bots running:', channels)
        await None

    def continue_running(self):
        return os.getenv('BOTMASTER_RUN', "yes") == "yes"

    async def main(self):
        await self.update_bots(once=True)
        print('loop')
        await asyncio.gather(
            self.handle_bots(),
            self.check_bots(),
            self.update_bots()
        )

    def run(self):
        asyncio.run(self.main())
