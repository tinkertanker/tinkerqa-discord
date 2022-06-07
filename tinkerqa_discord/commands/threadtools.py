# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord import Option
# noinspection PyPackageRequirements
from discord.ext import commands

import tinkerqa_discord
from tinkerqa_discord.commands.errors import NotInThread
from tinkerqa_discord.helpers import gen_embed, hacky_get_thread_starter_user_id


async def is_in_thread(ctx: discord.ApplicationContext):
    if isinstance(ctx.channel, discord.Thread):
        return True
    else:
        raise NotInThread(f"This command can only be used in a thread")


class ThreadTools(commands.Cog):
    def __init__(self, bot: tinkerqa_discord.TinkerQaDiscord):
        self.bot = bot
        self.qa_channel = self.bot.cfg.qa_channel
        self.helper_role = self.bot.cfg.helper_role

    @discord.slash_command(name="ask",
                           description="Creates a new thread in the #qa channel")
    async def create(self, ctx: discord.ApplicationContext,
                     question: Option(str, "What is your question?", required=True, default='')):
        """
        Handler for the /ask command to ask a question that will be linked to the Q&A channel
        :param ctx: context
        :param question: the question
        :return: nothing
        """
        if isinstance(ctx.channel, discord.Thread):
            raise commands.BadArgument("You are already in a thread!")
        if not question:
            await ctx.respond("Please try again, with an ACTUAL question")
            await ctx.delete(delay=3)
            return
        user_response = await ctx.respond("Please wait, creating the thread now")
        with ctx.typing():
            embed = gen_embed(question, ctx.author, ctx.guild.get_role(self.helper_role))
            # Note: The message is ULTRA fragile, please do not change it
            msg = await self.bot.get_channel(self.qa_channel).send(f"{ctx.author.mention}", embed=embed)
            thread = await msg.create_thread(name=question)
            await thread.send(content="Please reply below this message.")
            self.bot.logger.info(f"Created thread {thread.id}")
            await user_response.edit_original_message(content=f"Please see: {thread.mention}")
        await ctx.delete(delay=30)

    @discord.slash_command(name="close",
                           description="Closes the current thread")
    @commands.check(is_in_thread)
    async def close(self, ctx: discord.ApplicationContext):
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

    @discord.slash_command(name="delete_thread", description="Deletes the current thread")
    @commands.check(is_in_thread)
    @commands.has_permissions(manage_threads=True)
    async def delete_thread(self, ctx: discord.ApplicationContext):
        thread: discord.Thread = ctx.channel
        if thread.locked:
            await ctx.respond(f"This thread has been deleted by {ctx.author.mention}")
            await thread.delete()
            parent_msg = await thread.parent.fetch_message(thread.id)
            await parent_msg.delete()
            return
        else:
            await ctx.respond("A thread cannot be deleted if it is not locked and closed")
            await ctx.delete(delay=3)
            return


def setup(bot: tinkerqa_discord.TinkerQaDiscord):
    bot.add_cog(ThreadTools(bot))
