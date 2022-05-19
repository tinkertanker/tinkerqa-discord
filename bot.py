from typing import Union

import discord
from discord import Option
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig()
logger = logging.getLogger("tkqa-bot")
logger.setLevel(logging.INFO)
bot = discord.Bot()

guild = 976345115826212884
qa_channel = 976356366316875807
helper_role = 976669617097437208
embed_thumbnail_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/" \
                      "Icon-round-Question_mark.svg/2048px-Icon-round-Question_mark.svg.png"


def gen_embed(qn: str, author: Union[discord.User, discord.Member]) -> discord.Embed:
    embed = discord.Embed(title="QA Thread",
                          description="Please respond in the thread directly", color=0x2bff00)
    avatar_url = author.default_avatar.url
    if author.avatar:
        avatar_url = author.avatar.url
    embed.set_author(name=str(author),
                     icon_url=avatar_url)
    embed.set_thumbnail(
        url=embed_thumbnail_url)
    embed.add_field(name="Question", value=qn, inline=False)
    embed.set_footer(text="Generated by tinkerqa-discord v0.1.0")
    return embed


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}')


@bot.slash_command(guild_ids=[guild], name="mkthread",
                   description="Creates a new thread in the #qa channel")
async def create(ctx: discord.commands.context.ApplicationContext,
                 question: Option(str, "What is your question?", required=True, default='')):
    # TODO: this code needs to be refactored.
    if not question:
        await ctx.respond("Please try again, with an ACTUAL question")
        return
    user_response = await ctx.respond("Please wait, creating the thread now")
    with ctx.typing():
        embed = gen_embed(question, ctx.author)
        msg = await bot.get_channel(qa_channel).send(f"{ctx.author.mention}", embed=embed)
        thread = await msg.create_thread(name=question)
        logger.info(f"Created thread {thread.id}")
        await user_response.edit_original_message(content=f"Please see: {thread.jump_url}")


@bot.slash_command(guild_ids=[guild], name="close", description="Closes the current thread")
async def close(ctx: discord.commands.context.ApplicationContext):
    if not isinstance(ctx.channel, discord.Thread):
        await ctx.respond("This command can only be ran inside a thread")
        return
    thread: discord.Thread = ctx.channel
    if thread.locked:
        await ctx.respond("This command cannot be used inside a locked thread")
        return
    await ctx.respond("Thread closed")
    await thread.archive(locked=True)


if __name__ == "__main__":
    bot.run(os.environ.get('DISCORD_TOKEN'))
