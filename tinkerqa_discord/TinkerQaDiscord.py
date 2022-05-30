import discord
import logging
import os

from discord.ext import commands

from tinkerqa_discord.commands.errors import NotInThread

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

    async def on_application_command_error(self, ctx: discord.ApplicationContext,
                                           ex: discord.DiscordException) -> None:
        if isinstance(ex, NotInThread):
            await ctx.respond(f"{ctx.author.mention}, you must be in a thread to use this command")
            await ctx.delete(delay=3)
            return
        if isinstance(ex, commands.MissingPermissions):
            self.logger.warning(f"{ctx.author.name} tried to use a privileged command. Lacks: {ex.missing_permissions}")
            await ctx.respond(f"{ctx.author.mention}, you do not have permission to use this command")
            await ctx.delete(delay=3)
            return
        self.logger.error(f"{ctx.author} threw an error: {ex}")
        await ctx.respond(f"{ctx.author.mention}: Could not process that command.")
        await ctx.delete(delay=3)
