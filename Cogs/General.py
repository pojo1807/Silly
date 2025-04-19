from discord.ext import commands
from discord import app_commands


class General(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))