from __init__ import BetterCommand
from discord.ext import commands
from Utils.Helper import Emojis

class Utilities(commands.Cog, name="Meow Utilities"):
    def __init__(self, bot):
        self.bot = bot
        self.Emojis = Emojis
        self.Emoji = self.Emojis.UIA_Spinning


    # Slash command for /help
    @BetterCommand(name="help", description="Let the silliest cat help you!")
    async def slash_help(self, interaction: commands.Context, command: str = None):
        # Create a context from the interaction
        ctx = await commands.Context.from_interaction(interaction)
        # Set the invoked command to help
        ctx.invoked_with = "help"
        # Pass the command argument if provided
        ctx.args = [ctx, command] if command else [ctx]
        
        # Invoke the custom HelpCommand
        await self.bot.help_command.command_callback(ctx, command=command)
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Utilities(bot))