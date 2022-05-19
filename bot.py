from typing import Union

# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
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


def gen_embed(qn: str, author: Union[discord.User, discord.Member],
              helper_role_ping: discord.Role) -> discord.Embed:
    """
    Generates the embed template for the message and thread to be posted in the Q&A channel
    :param qn: The question
    :param author: The author of the question
    :param helper_role_ping: Role of helpers to ping
    :return: The embed template
    """
    embed = discord.Embed(title="QA Thread",
                          description=f"Please respond in the thread directly.\n"
                                      f"{author.mention}, please provide additional context if needed.\n"
                                      f"\n"
                                      f"{helper_role_ping.mention}, please provide assistance if possible",
                          color=0x2bff00)
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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the QA channel"))
    logger.info(f'Logged in as {bot.user.name}')


@bot.slash_command(guild_ids=[guild], name="ask",
                   description="Creates a new thread in the #qa channel")
async def create(ctx: discord.commands.context.ApplicationContext,
                 question: Option(str, "What is your question?", required=True, default='')):
    """
    Handler for the /ask command to ask a question that will be linked to the Q&A channel
    :param ctx: context
    :param question: the question
    :return: nothing
    """
    if not question:
        await ctx.respond("Please try again, with an ACTUAL question")
        await ctx.delete(delay=3)
        return
    user_response = await ctx.respond("Please wait, creating the thread now")
    with ctx.typing():
        embed = gen_embed(question, ctx.author, ctx.guild.get_role(helper_role))
        # Note: The message is ULTRA fragile, please do not change it
        msg = await bot.get_channel(qa_channel).send(f"{ctx.author.mention}", embed=embed)
        thread = await msg.create_thread(name=question)
        logger.info(f"Created thread {thread.id}")
        await user_response.edit_original_message(content=f"Please see: {thread.jump_url}")


async def get_first_message(channel: discord.Thread) -> discord.Message:
    """
    Retrieves the first message in a thread
    :param channel: The thread to retrieve the first message from
    :return: The first message
    """
    async for msg in channel.history(limit=1, oldest_first=True):
        return msg


@bot.slash_command(guild_ids=[guild], name="delete_thread", description="Deletes the current thread")
async def delete_thread(ctx: discord.commands.context.ApplicationContext):
    if not isinstance(ctx.channel, discord.Thread):
        await ctx.respond("This command can only be used in a thread")
        await ctx.delete(delay=3)
        return
    if not ctx.author.guild_permissions.manage_threads:
        await ctx.author.send(content="You do not have the permission to delete threads")
        await ctx.delete(delay=3)
        return
    thread: discord.Thread = ctx.channel
    if thread.locked:
        # await ctx.author.send(content="I have deleted the locked thread")
        await ctx.respond("This thread has been deleted")
        await thread.delete()
        return
    else:
        await ctx.respond("A thread cannot be deleted if it is not locked and closed")
        return


class HackyException(Exception):
    pass


async def hacky_get_thread_starter_user_id(thread: discord.Thread) -> int:
    """
    This function is a hack to grab the "author" of the thread.
    Note this is extremely fragile and very highly dependent on how the message was sent.

    This hack is needed because the first_msg does NOT contain mentions, even if I
    explicitly mention the author. As such, I am forced to parse it as such

    :param thread: The thread
    :return: The "author's" user ID
    :raises HackyException: If the message is empty
    :raises ValueError: If the message is in the wrong format
    """
    first_msg = await get_first_message(thread)
    if not first_msg.system_content:
        # await ctx.respond("Internal error, please contact devs. Error code: empty-content")
        raise HackyException("Empty content")
    contents = first_msg.system_content
    contents = contents.replace("<@", "").replace(">", "")  # awful hack
    return int(contents)


@bot.slash_command(guild_ids=[guild], name="close", description="Closes the current thread")
async def close(ctx: discord.commands.context.ApplicationContext):
    if not isinstance(ctx.channel, discord.Thread):
        await ctx.respond("This command can only be ran inside a thread")
        await ctx.delete(delay=3)
        return

    thread: discord.Thread = ctx.channel
    question_author_id = await hacky_get_thread_starter_user_id(thread)
    if thread.locked:
        await ctx.respond("This command cannot be used inside a locked thread")
        await ctx.delete(delay=3)
        return

    if ctx.author.guild_permissions.manage_threads:
        await ctx.respond("Thread closed by moderator")
    elif question_author_id == int(ctx.author.id):
        await ctx.respond("Thread closed by OP")
    else:
        await ctx.respond("You do not have the permission to close this thread")
        await ctx.delete(delay=3)
        return
    await thread.archive(locked=True)


# @bot.slash_command(guild_ids=[guild], name="clear_channel",
#                    description="Deletes all the messages present in the channel")
# async def clear_channel(ctx: discord.commands.context.ApplicationContext):
#     if isinstance(ctx.channel, discord.TextChannel):
#         chan: discord.TextChannel = ctx.channel
#         await chan.delete_messages([m async for m in chan.history(limit=200)])
#         await ctx.respond("Done.")
#     else:
#         await ctx.respond("Can't delete")


if __name__ == "__main__":
    bot.run(os.environ.get('DISCORD_TOKEN'))
