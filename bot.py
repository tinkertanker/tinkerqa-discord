import discord
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.slash_command(guild_ids=[976345115826212884])
async def test(ctx):
    await ctx.respond("Hello World!")


if __name__ == "__main__":
    bot.run(os.environ.get('DISCORD_TOKEN'))
