import discord
from discord import Option
from discord.ext import commands

import tinkerqa_discord
from tinkerqa_discord.helpers import gen_embed, hacky_get_thread_starter_user_id


# guild = configuration["role_ids"]["guild"]
# qa_channel = configuration["role_ids"]["qa_channel"]
# helper_role = configuration["role_ids"]["helper_role"]


class ThreadTools(commands.Cog):
    def __init__(self, bot: tinkerqa_discord.TinkerQaDiscord):
        self.bot = bot
        # self.guild = self.bot.config["role_ids"]["guild"]
        self.qa_channel = self.bot.config["role_ids"]["qa_channel"]
        self.helper_role = self.bot.config["role_ids"]["helper_role"]

    @discord.slash_command(name="ask",
                           guild_ids=[tinkerqa_discord.TinkerQaDiscord.guild],
                           description="Creates a new thread in the #qa channel")
    async def create(self, ctx: discord.commands.context.ApplicationContext,
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
            embed = gen_embed(question, ctx.author, ctx.guild.get_role(self.helper_role))
            # Note: The message is ULTRA fragile, please do not change it
            msg = await self.bot.get_channel(self.qa_channel).send(f"{ctx.author.mention}", embed=embed)
            thread = await msg.create_thread(name=question)
            self.bot.logger.info(f"Created thread {thread.id}")
            await user_response.edit_original_message(content=f"Please see: {thread.mention}")
        await ctx.delete(delay=30)

    @discord.slash_command(guild_ids=[tinkerqa_discord.TinkerQaDiscord.guild], name="close", description="Closes the current thread")
    async def close(self, ctx: discord.commands.context.ApplicationContext):
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

    @discord.slash_command(guild_ids=[tinkerqa_discord.TinkerQaDiscord.guild],
                           name="delete_thread", description="Deletes the current thread")
    async def delete_thread(self, ctx: discord.commands.context.ApplicationContext):
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.respond("This command can only be used in a thread")
            await ctx.delete(delay=3)
            return
        if not ctx.author.guild_permissions.manage_threads:
            await ctx.respond(f"{ctx.author.mention}, you do not have permission to delete threads")
            await ctx.delete(delay=3)
            return
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
