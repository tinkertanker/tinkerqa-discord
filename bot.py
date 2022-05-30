import logging
import os

from dotenv import load_dotenv

from tinkerqa_discord import TinkerQaDiscord


if __name__ == "__main__":
    load_dotenv()
    bot = TinkerQaDiscord()
    bot.run(os.environ.get('DISCORD_TOKEN'))
