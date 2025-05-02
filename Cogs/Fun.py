import logging
import re
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Select
from discord.components import SelectOption

import random as rd

from Cogs.__init__ import BetterCommand, HelpFormat

from Utils.Helper import Emojis
from Utils.Globals import ASCII_CATS_BIG, ASCII_CATS_SMALL, ASCII_CATS_ONELINE, PREFIX

logger = logging.getLogger(__name__)


class Fun(commands.Cog):
    Emoji = Emojis.InsaneArhh

    def __init__(self, bot):
        self.bot = bot
        self.Emojis = Emojis

    @BetterCommand(
        name="ascii_cat",
        description="Send randomly ascii cat",
        brief="Send randomly **ascii art of cat**",
        help=f"""Meow randomly an **ascii art of cat** with **"New!"** button and **"Size"** select menu!""",
        usage=f"""This is how you can use it to **get ascii art of cat**:
        
{HelpFormat(
    f"{PREFIX}ascii_cat",
    Required={
        "size": {
            "": "The size of the ascii cat (Default: **Random**)",
            "Big": "Big big big cat!!!",
            "Small": "Small cute kitten (^.^)",
            "One-Line": "One-line ascii cats (=^.^=)",
        },
    },
    Optional={
        "ephemeral": {
            "": "Please send me secretly (only me can see it) (Default: **False**)",
            "True": "Yes",
            "False": "No",
        },
    },
)}""",
        aliases=["meowart"],
        dm_permission=True,
    )
    @commands.cooldown(2, 15, commands.BucketType.user)
    @app_commands.choices(
        size=[
            app_commands.Choice(name="Random", value="Random"),
            app_commands.Choice(name="Big", value="Big"),
            app_commands.Choice(name="Small", value="Small"),
            app_commands.Choice(name="One-Line", value="One-Line"),
        ]
    )
    @app_commands.user_install()
    async def ascii_cat(
        self, ctx: commands.Context, *, size: str = "Random", ephemeral: bool = False
    ):
        """
        Args:
            ctx (commands.Context): Context of the command
            size (str, optional): Size of the ascii cat. (Default: "Random", Optional)
            ephemeral (bool, optional): Please send me secretly (only me can see it). (Default: False, Optional)
        """
        ascii_arts_map = {
            "Random": lambda: rd.choice(
                [ASCII_CATS_BIG, ASCII_CATS_SMALL, ASCII_CATS_ONELINE]
            ),
            "Big": lambda: ASCII_CATS_BIG,
            "Small": lambda: ASCII_CATS_SMALL,
            "One-Line": lambda: ASCII_CATS_ONELINE,
        }

        ascii_arts = ascii_arts_map.get(size)()
        is_oneline = ascii_arts is ASCII_CATS_ONELINE

        the_symbol = "`" if is_oneline else "```"
        newline = "\n" if is_oneline else ""

        display_name = (
            ctx.author.display_name[:9] + "..."
            if len(ctx.author.display_name) > 12
            else ctx.author.display_name
        )
        raw_ascii_art = rd.choice(ascii_arts)

        result = f"{the_symbol}{raw_ascii_art}{the_symbol}{newline}\n-# {self.Emojis.random()} {display_name} requested this ascii cat."

        if len(result) > 2000:
            ascii_art = raw_ascii_art[: 1990 - len(result) + len(raw_ascii_art)] + "..."
            result = f"{the_symbol}{ascii_art}{the_symbol}{newline}\n-# {self.Emojis.random()} {display_name} requested this ascii cat."
            is_too_long = True
        else:
            is_too_long = False

        class NewButton(Button):
            def __init__(self, fun_cog, ctx, current_size):
                super().__init__(
                    label="New",
                    style=discord.ButtonStyle.primary,
                    emoji=Emojis.UIA_Spinning,
                )
                self.fun_cog = fun_cog
                self.ctx = ctx
                self.current_size = current_size

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(
                        f"{Emojis.CatScare} You can't use this button!", ephemeral=True
                    )
                    return

                logger.info(f"Current size: {self.current_size}")
                new_ascii_arts = ascii_arts_map.get(self.current_size)()

                is_oneline = new_ascii_arts is ASCII_CATS_ONELINE

                the_symbol = "`" if is_oneline else "```"
                newline = "\n" if is_oneline else ""
                new_ascii_art = rd.choice(new_ascii_arts)

                new_result = f"{the_symbol}{new_ascii_art}{the_symbol}{newline}\n-# {self.fun_cog.Emojis.CatSmile} {display_name} requested this ascii cat."

                if len(new_result) > 2000:
                    new_ascii_art = (
                        new_ascii_art[: 1990 - len(new_result) + len(new_ascii_art)]
                        + "..."
                    )
                    new_result = f"{the_symbol}{new_ascii_art}{the_symbol}{newline}\n-# {self.fun_cog.Emojis.CatSmile} {display_name} requested this ascii cat."

                await interaction.message.edit(content=new_result)
                await interaction.response.defer()

        class SizeSelect(Select):
            def __init__(self, fun_cog, ctx):
                super().__init__(
                    placeholder="Re-generate ascii cat with different size!",
                    options=[
                        SelectOption(
                            label="Random",
                            value="Random",
                            description="Random size from my collection",
                        ),
                        SelectOption(
                            label="Big", value="Big", description="Big big big cat!!!"
                        ),
                        SelectOption(
                            label="Small",
                            value="Small",
                            description="Small cute kitten (^.^)",
                        ),
                        SelectOption(
                            label="One-Line",
                            value="One-Line",
                            description="One-line ascii cats (=^.^=)",
                        ),
                    ],
                    min_values=1,
                    max_values=1,
                )
                self.fun_cog = fun_cog
                self.ctx = ctx

            async def callback(self, interaction: discord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message(
                        f"{self.fun_cog.Emojis.CatScare} You can't use this select menu!",
                        ephemeral=True,
                    )
                    return

                new_size = self.values[0]
                logger.info(f"New size: {new_size}")
                # Update the button's size reference
                for child in self.view.children:
                    if isinstance(child, NewButton):
                        child.current_size = new_size

                new_ascii_arts = ascii_arts_map.get(new_size)()
                is_oneline = new_ascii_arts is ASCII_CATS_ONELINE

                the_symbol = "`" if is_oneline else "```"
                newline = "\n" if is_oneline else ""

                new_ascii_art = rd.choice(new_ascii_arts)
                new_result = f"{the_symbol}{new_ascii_art}{the_symbol}{newline}\n-# {self.fun_cog.Emojis.CatSmile} {display_name} requested this ascii cat."

                if len(new_result) > 2000:
                    new_ascii_art = (
                        new_ascii_art[: 1990 - len(new_result) + len(new_ascii_art)]
                        + "..."
                    )
                    new_result = f"{the_symbol}{new_ascii_art}{the_symbol}{newline}\n-# {self.fun_cog.Emojis.CatSmile} {display_name} requested this ascii cat."

                try:
                    await interaction.message.edit(content=new_result)
                    await interaction.response.defer()
                except discord.HTTPException:
                    pass

        class AsciiCatView(View):
            def __init__(self, fun_cog, ctx, size, ephemeral):
                super().__init__(timeout=180)  # 3 minutes
                self.fun_cog = fun_cog
                self.ctx = ctx
                self.ephemeral = ephemeral
                self.message = None

                self.add_item(NewButton(fun_cog, ctx, size))
                self.add_item(SizeSelect(fun_cog, ctx))

            async def on_timeout(self):
                self.clear_items()
                try:
                    embed = discord.Embed(
                        description=f"-# {self.fun_cog.Emojis.NerdCat} This ascii cat message has expired. **But don't worry, just use the command again!**",
                        color=discord.Color.yellow(),
                    )
                    embed.set_author(
                        name=f"{ctx.author.display_name} Requested this ascii cat. (Expired)",
                        icon_url=ctx.author.display_avatar.url,
                    )

                    if self.message:
                        await self.message.edit(
                            content=None, embed=embed, view=None, delete_after=10
                        )

                except discord.HTTPException:
                    pass

        view = AsciiCatView(self, ctx, size, ephemeral)
        message = await ctx.send(result, ephemeral=ephemeral, view=view)
        view.message = message

        if is_too_long and message:
            await message.reply(
                "> Fact: **This ascii cat is too long to be displayed in the message**.\n> Please report this to my owner :P.",
                silent=True,
            )

    @BetterCommand(
        name="say",
        description="Let me say something for you with meowified!",
        brief="Let me say something for you with **purrrfect _silly_ style**!",
        help=f"""Let me say what you want with **meowified** and **sillified**! Example:
-# __BEFORE__
> Hi everyone, my name is Silly, I'm a silly cat and I love people!

-# __MEOWIFIED & SILLIFIED__
> `(=^･^=)` nyaa~ everycat, my name is Silly, I'm a silly cat and I meow hoomans! :3""",
        usage=f"""This is how you can use it to **get meowified** and **sillified** message:
{HelpFormat(
    f"{PREFIX}say",
    Required={
        "message": {
            "": "The message to say, will be meowified and sillified",
        },
    },
    Optional={
        "ephemeral": {
            "": "Please send me secretly (only me can see it) (Default: **False**)",
            "True": "Yes",
            "False": "No",
        },
    },
)}""",
    )
    async def say(
        self, ctx: commands.Context, *, message: str, ephemeral: bool = False
    ) -> None:
        """
        Args:
            ctx (commands.Context): Context of the command
            message (str): The message to say, will be meowified and sillified
            ephemeral (bool, optional): Please send me secretly (only me can see it). (Default: False, Optional)
        """
        # Sanitize and check message length
        if len(message) > 1900:
            await ctx.send(
                f"-# {self.Emojis.CatScare} Whoa, that's a chunky message! Try something shorter so I can meow it out.",
                ephemeral=True,
            )
            return

        cat_prefixes: list[str] = [
            lambda: f"`{rd.choice(ASCII_CATS_ONELINE)}`",
            lambda: self.Emojis.random(),
        ]
        message = f"{rd.choice(cat_prefixes)()} {message}"

        # New, more creative and non-repetitive replacements
        replacements: dict[str, str] = {
            r"\bhello\b": "meowdy",
            r"\beveryone\b": "everycat",
            r"\bpeople\b": "hoomans",
            r"\bguy\b": "cat",
            r"\bguys\b": "cats",
            r"\byall\b": "cats",
            r"\bhi\b": "nyaa~",
            r"\bhey\b": "meowllo",
            r"\bgood morning\b": "purr-morning",
            r"\bgood night\b": "catnap time",
            r"\bbye\b": "meowbye",
            r"\bgoodbye\b": "see mew later",
            r"\bsee you\b": "catch ya later",
            r"\bthanks\b": "paws up, thanks!",
            r"\bthank you\b": "purrreciate it",
            r"\bplease\b": "purrlease",
            r"\bawesome\b": "claw-some",
            r"\bcool\b": "cat-tastic",
            r"\bfunny\b": "hiss-terical",
            r"\bhappy\b": "feline fine",
            r"\bsad\b": "tail down",
            r"\bproblem\b": "cat-astrophe",
            r"\bparty\b": "catnip rave",
            r"\bcry\b": "mewl",
            r"\blaugh\b": "purr-giggle",
            r"\bbeautiful\b": "purrty",
            r"\bpretty\b": "purrty",
            r"\bfriend\b": "furriend",
            r"\bfood\b": "treats",
            r"\bhome\b": "cat tree",
            r"\bhouse\b": "cat castle",
            r"\bsleep\b": "catnap",
            r"\bnap\b": "catnap",
            r"\bwalk\b": "prowl",
            r"\bright now\b": "right meow",
            r"\blater\b": "after my nap",
            r"\bsoon\b": "after a catnap",
            r"\bnever\b": "not in nine lives",
            r"\balways\b": "furrever",
            r"\bforever\b": "furrever",
            r"\blove\b": "meow",
            r"\bpolice\b": "paw-lice",
            r"\bowner\b": "can opener",
            r"\bwork\b": "nap time",
            r"\bwin\b": "catch the red dot",
            r"\blose\b": "miss the laser",
            r"\bscared\b": "spooked like a kitten",
            r"\bbored\b": "cat loaf mode",
        }

        # To avoid overlapping/duplicate replacements, sort by length descending
        sorted_replacements = sorted(replacements.items(), key=lambda x: -len(x[0]))
        for pattern, replacement in sorted_replacements:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)

        # Add a random silly suffix
        suffixes: list[str] = [
            "~nya",
            "purr~",
            "uwu",
            ":3",
            "✨",
            "😸",
            "🐾",
            "meow~",
            "mrrp",
            "mewmew",
            "rawr",
            "(*≧ω≦)",
            "ฅ^•ﻌ•^ฅ",
        ]
        message += f" *{rd.choice(suffixes)}*"
        if len(message) > 2000:
            message = message[:1970] + "...\n-# Too long, sorry!"

        await ctx.send(message, mention_author=True, ephemeral=ephemeral)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
