import logging
import os.path

import discord

try:
    from yaml import load, CLoader as Loader
except ImportError:
    from yaml import load, Loader


class TinkerQaDiscord(discord.Bot):

    _this_file_dir = os.path.dirname(os.path.abspath(__file__))
    _config_path = os.path.abspath(os.path.join(_this_file_dir, "..", "config.yml"))
    conf = load(open(_config_path, 'r'), Loader)
    guild = conf["guild"]

    def __init__(self, *args, **options):
        super().__init__(*args, **options)
        self.config = self.conf
        self._setup_logger()
        self.load_extension("tinkerqa_discord.commands.threadtools")

    def _setup_logger(self):
        logging.basicConfig()
        self.logger = logging.getLogger("tkqa-bot")
        self.logger.setLevel(logging.INFO)

    async def on_ready(self):
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the QA channel"))
        self.logger.info(f'Logged in as {self.user.name}')
