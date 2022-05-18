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
    user_response = await ctx.respond("Please wait, creating the thread now")
    await ctx.trigger_typing()
    embed = discord.Embed(title="QA Thread", description="Please respond in the thread directly")
    avatar_url = ctx.author.default_avatar.url
    if ctx.author.avatar:
        avatar_url = ctx.author.avatar.url
    embed.set_author(name=str(ctx.author),
                     icon_url=avatar_url)
    embed.set_thumbnail(
        url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Icon-round-Question_mark.svg/2048px-Icon-round"
            "-Question_mark.svg.png")
    embed.add_field(name="Question", value=question, inline=False)
    embed.set_footer(text="Generated by tinkerqa-discord v0.1.0")
    msg = await bot.get_channel(qa_channel).send(embed=embed)
    thread = await msg.create_thread(name=question)
    await user_response.edit_original_message(content=f"Please see: {thread.jump_url}")


if __name__ == "__main__":
    bot.run(os.environ.get('DISCORD_TOKEN'))
