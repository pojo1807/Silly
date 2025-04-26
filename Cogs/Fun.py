import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Select
from discord.components import SelectOption

import random as rd

from Cogs.__init__ import BetterCommand, HelpFormat

from Utils.Helper import Emojis
from Utils.Globals import ASCII_CATS_BIG, ASCII_CATS_SMALL, ASCII_CATS_ONELINE, PREFIX

class Fun(commands.Cog):
    Emoji = Emojis.InsaneArhh
    def __init__(self, bot):
        self.bot = bot
        self.Emojis = Emojis
        
    @BetterCommand(
        name="ascii_cat",
        description="Send randomly ascii cat",
        brief="Send randomly **ascii cat**",
        help=f"""Meowww! {Emojis.CatEatingChips} Time to show you my ascii art collection!

I have a lot of ascii cats in my collection, and I will show you one of them randomly!
You can choose the size of the ascii cat:
- `Random`: I will choose randomly from all sizes
- `Big`: Big ascii cat (>.<)
- `Small`: Small ascii cat (^.^)
- `One-Line`: One line ascii cat (=^.^=)

*purrrr... Just tell me what size you want and I will show you one of my ascii cats! ฅ^•ﻌ•^ฅ*""",
        usage=f"""This is how you can use it to **get ascii cat**:
{HelpFormat(f"{PREFIX}ascii_cat", Optional=["size", "ephemeral"])}""",
        aliases=["meowart"]
    )
    @commands.cooldown(2, 4, commands.BucketType.user)
    @app_commands.choices(
        size=[
            app_commands.Choice(name="Random", value="Random"),
            app_commands.Choice(name="Big", value="Big"),
            app_commands.Choice(name="Small", value="Small"),
            app_commands.Choice(name="One-Line", value="One-Line")
        ]
    )
    @app_commands.user_install()
    async def ascii_cat(self, ctx: commands.Context, *, size: str = "Random", ephemeral: bool = False):
        """Send randomly ascii cat

        Args:
            ctx (commands.Context): The context of the command
            size (str, optional): Size of the ascii cat. (Default: Random)
            ephemeral (bool, optional): Please send me secretly (only me can see it). (Default: False)
        """
        await self._send_ascii_cat(ctx, size, ephemeral)

    async def _send_ascii_cat(self, ctx: commands.Context, size: str = "Random", ephemeral: bool = False):
        """Internal function to send ascii cat

        Args:
            ctx (commands.Context): The context of the command
            size (str, optional): Size of the ascii cat. (Default: Random)
            ephemeral (bool, optional): Please send me secretly (only me can see it). (Default: False)
        """
        if size == "Random":
            ASCII_ARTS = rd.choice([ASCII_CATS_BIG, ASCII_CATS_SMALL, ASCII_CATS_ONELINE])
        elif size == "Big":
            ASCII_ARTS = ASCII_CATS_BIG
        elif size == "Small":
            ASCII_ARTS = ASCII_CATS_SMALL
        elif size == "One-Line":
            ASCII_ARTS = ASCII_CATS_ONELINE
            
        the_symbol = "`" if ASCII_ARTS is ASCII_CATS_ONELINE else "```"
        newline = "\n" if ASCII_ARTS is ASCII_CATS_ONELINE else ""
        
        isTooLong = False
        display_name = ctx.author.display_name
        if len(display_name) > 12:
            display_name = display_name[:9] + "..."
        raw_ascii_art = rd.choice(ASCII_ARTS) # The raw ascii art without any decoration
        result = f"{the_symbol}{raw_ascii_art}{the_symbol}{newline}\n-# {self.Emojis.random()} {display_name} requested this ascii cat." # The result message
        if len(result) > 2000:
            isTooLong = True
            ascii_art = raw_ascii_art[:1990 - len(result) + len(raw_ascii_art)] + "..." # the ascii art that will be displayed in the message
            result = f"{the_symbol}{ascii_art}{the_symbol}{newline}\n-# {self.Emojis.random()} {display_name} requested this ascii cat."

        # Create the New button
        class NewButton(Button):
            def __init__(self, fun_cog, ctx, size):
                super().__init__(label="New", style=discord.ButtonStyle.primary, emoji=Emojis.UIA_Spinning)
                self.fun_cog = fun_cog
                self.ctx = ctx
                self.size = size
                        
            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(f"{Emojis.CatScare} You can't use this button!", ephemeral=True)
                    return
                
                # Generate new ascii art
                if size == "Random":
                    new_ascii_arts = rd.choice([ASCII_CATS_BIG, ASCII_CATS_SMALL, ASCII_CATS_ONELINE])
                elif size == "Big":
                    new_ascii_arts = ASCII_CATS_BIG
                elif size == "Small":
                    new_ascii_arts = ASCII_CATS_SMALL
                else:
                    new_ascii_arts = ASCII_CATS_ONELINE
                
                the_symbol = "`" if new_ascii_arts is ASCII_CATS_ONELINE else "```"
                newline = "\n" if new_ascii_arts is ASCII_CATS_ONELINE else ""
                new_ascii_art = rd.choice(new_ascii_arts)
                while new_ascii_art == raw_ascii_art:
                    new_ascii_art = rd.choice(new_ascii_arts)
                
                new_result = f"{the_symbol}{new_ascii_art}{the_symbol}{newline}\n-# {self.fun_cog.Emojis.CatSmile} {display_name} requested this ascii cat."
                
                if len(new_result) > 2000:
                    new_ascii_art = new_ascii_art[:1990 - len(new_result) + len(new_ascii_art)] + "..."
                    new_result = f"{the_symbol}{new_ascii_art}{the_symbol}{newline}\n-# {self.fun_cog.Emojis.CatSmile} {display_name} requested this ascii cat."
                
                await interaction.message.edit(content=new_result)
                await interaction.response.defer()
                
        # Create the Select
        class SizeSelect(Select):
            def __init__(self, fun_cog, ctx, size):
                super().__init__(
                    placeholder=f"Re-generate ascii cat with different size!",
                    options=[
                        SelectOption(label="Random", value="Random", description="Random size from my collection"),
                        SelectOption(label="Big", value="Big", description="Big big big cat!!!"),
                        SelectOption(label="Small", value="Small", description="Small cute kitten (^.^)"),
                        SelectOption(label="One-Line", value="One-Line", description="One-line ascii cats (=^.^=)")
                    ],
                    min_values=1,
                    max_values=1
                )
                self.fun_cog = fun_cog
                self.ctx = ctx
                self.size = size


            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(f"{self.fun_cog.Emojis.CatScare} You can't use this select menu!", ephemeral=True)
                    return

                new_size = self.values[0]
                
                # Generate new ascii art
                if new_size == "Random":
                    new_ascii_arts = rd.choice([ASCII_CATS_BIG, ASCII_CATS_SMALL, ASCII_CATS_ONELINE])
                elif new_size == "Big":
                    new_ascii_arts = ASCII_CATS_BIG
                elif new_size == "Small":
                    new_ascii_arts = ASCII_CATS_SMALL
                else:
                    new_ascii_arts = ASCII_CATS_ONELINE
                
                the_symbol = "`" if new_ascii_arts is ASCII_CATS_ONELINE else "```"
                newline = "\n" if new_ascii_arts is ASCII_CATS_ONELINE else ""
                new_ascii_art = rd.choice(new_ascii_arts)
                while new_ascii_art == raw_ascii_art:
                    new_ascii_art = rd.choice(new_ascii_arts)
                
                new_result = f"{the_symbol}{new_ascii_art}{the_symbol}{newline}\n-# {self.fun_cog.Emojis.CatSmile} {display_name} requested this ascii cat."
                
                if len(new_result) > 2000:
                    new_ascii_art = new_ascii_art[:1990 - len(new_result) + len(new_ascii_art)] + "..."
                    new_result = f"{the_symbol}{new_ascii_art}{the_symbol}{newline}\n-# {self.fun_cog.Emojis.CatSmile} {display_name} requested this ascii cat."
                
                await interaction.message.edit(content=new_result)
                await interaction.response.defer()
                
        class AsciiCatView(View):
            def __init__(self, fun_cog, ctx, size, ephemeral):
                super().__init__(timeout=180)
                self.fun_cog = fun_cog
                self.ctx = ctx
                self.size = size
                self.ephemeral = ephemeral
                self.message: discord.Message = None 

                self.add_item(NewButton(fun_cog, ctx, size))
                self.add_item(SizeSelect(fun_cog, ctx, ephemeral))

            async def on_timeout(self):
                self.clear_items()
                try:
                    embed = discord.Embed(
                        description=f"# {self.fun_cog.Emojis.NerdCat} This ascii cat message has expired.\n**But don't worry, just use the command again!**\n-# {self.fun_cog.Emojis.random(10)}",
                        color=discord.Color.yellow()
                    )
                    embed.set_author(name=ctx.author.display_name + " Requested this ascii cat. (Expired)", icon_url=ctx.author.display_avatar.url)
                    
                    
                    if self.message:
                        await self.message.edit(content=None, embed=embed, view=None)
                except discord.HTTPException:
                    pass
                
        if ctx.interaction.guild != None:
            # create view and add button, select
            view = AsciiCatView(self, ctx, size, ephemeral)
            
            
            message = await ctx.send(result, ephemeral=ephemeral, view=view)
            view.message = message
        else:
            message = await ctx.send(result, ephemeral=ephemeral)
            
        if isTooLong:
            await message.reply(f"> Fact: **This ascii cat is too long to be displayed in the message**.\n> Please report this to my owner :P.", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))

