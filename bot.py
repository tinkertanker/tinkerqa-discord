import os

from dotenv import load_dotenv

from tinkerqa_discord import TinkerQaDiscord, Config

if __name__ == "__main__":
    load_dotenv()
    cfg = Config(guild=os.getenv("GUILD_QA_CHANNEL"),
                 qa_channel=os.getenv("GUILD_QA_CHANNEL"),
                 helper_role=os.getenv("GUILD_HELPER_ROLE"))
    bot = TinkerQaDiscord(cfg)
    bot.run(os.environ.get('DISCORD_TOKEN'))
