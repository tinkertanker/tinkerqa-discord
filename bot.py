import discord
from discord import Option
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

guilds = [976345115826212884]
qa_channel = 976356366316875807

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.slash_command(guild_ids=guilds, name="mkthread",
                   description="Creates a new thread in the #qa channel")
async def create(ctx: discord.commands.context.ApplicationContext,
                 question: Option(str, "What is your question?", required=True, default='')):
    if not question:
        await ctx.respond("Please try again, with an ACTUAL question")
        return
    await ctx.respond(f"Your question is: {question}. "
                      f"I have created a new thread for you in {bot.get_channel(qa_channel).mention}")
    await bot.get_channel(qa_channel).send(question)


if __name__ == "__main__":
    bot.run(os.environ.get('DISCORD_TOKEN'))
