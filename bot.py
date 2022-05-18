import discord
from dotenv import load_dotenv
import os

load_dotenv()

bot = discord.Bot()


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.slash_command(guild_ids=[''])
async def slash_command(ctx):
    await ctx.respond("Hello World!")


if __name__ == "__main__":
    bot.run(os.environ.get('DISCORD_TOKEN'))
