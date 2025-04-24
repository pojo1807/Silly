from discord.ext import commands
import discord
from Cogs.__init__ import BetterCommand, HelpFormat


from Utils.Helper import Emojis
from Utils.Globals import PREFIX

import datetime
import re
import logging
import psutil
import random as rd
import asyncio
class General(commands.Cog):
    bot: commands.Bot
    Emoji = Emojis.Guh

    def __init__(self, bot):
        self.bot = bot
        self.Logger = logging.getLogger("silly")
        self.Emojis = Emojis
        
        
    # ---------------------------------------------------------------------------- #
    #                                ERROR LISTENER                                #
    # ---------------------------------------------------------------------------- #
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        # ---------------------------------------------------------------------------- #
        #                                CommandNotFound                               #
        # ---------------------------------------------------------------------------- #
        if isinstance(error, commands.CommandNotFound):
            self.Logger.warning(f'[grey70]{ctx.author.name}[/] '
                                f'- COMMAND NOT FOUND in [bold underline link=https://discordapp.com/channels/{ctx.message.guild.id}/{ctx.channel.id}/{ctx.message.id}]#{ctx.channel.name}[/bold underline link]: '
                                f'[grey50]{PREFIX}{ctx.invoked_with}[/]')
            
            embed = discord.Embed(
                title=f"{self.Emojis.SecurityCat} ・ Command Not Found",
                description=f"*Meow~?* I couldn't find that command!\nPlease check the command name and try again.",
                color=discord.Color.red()
            )
            
            embed.set_footer(text=f"Tip: try {PREFIX}help to see what I actually understand! 😼")
            embed.set_thumbnail(url="https://tenor.com/view/huh-cat-pissi-twitch-7tv-gif-7223094372649290081")
            
            await ctx.send(embed=embed)
            
        # ---------------------------------------------------------------------------- #
        #                            MissingRequiredArgument                           #
        # ---------------------------------------------------------------------------- #
        elif isinstance(error, commands.MissingRequiredArgument):
            def strip_ansi(text: str) -> str:
                return re.sub(r'\x1b\[[0-9;]*m', '', text) # Remove ANSI escape codes
            cmd_usage = f"{PREFIX}{ctx.invoked_with} "

            params = []
            underline = []

            for param in ctx.command.clean_params.values():
                if param.annotation == discord.Member:
                    param_str = f"\033[2;31m<@{param.name}>\033[0m"
                else:
                    param_str = f"\033[2;32m[{param.name}]\033[0m"

                params.append(param_str)

                visible_len = len(strip_ansi(param_str))

                if param.name == error.param.name:
                    underline.append('^' * visible_len)
                else:
                    underline.append(" " * visible_len)

            usage_line = cmd_usage + " ".join(params)
            underline_line = " " * len(cmd_usage) + " ".join(underline)
            
            self.Logger.warning(f'[grey70]{ctx.author.name}[/] '
                                f'- MISSING REQUIRED ARGUMENT in [bold underline link=https://discordapp.com/channels/{ctx.message.guild.id}/{ctx.channel.id}/{ctx.message.id}]#{ctx.channel.name}[/bold underline link]: '
                                f'[grey50]{error.param.name} ({PREFIX}{ctx.invoked_with})[/]')
            embed = discord.Embed(
                description=f"""# {self.Emojis.SecurityCat} ・ Missing Argument
**Sorry, I don't *meow* what you are _typing_**...
I need a **little more information** to help you with that command!
Here is what I need:
```ansi
[2;31m<>[0m is [2;31mRequired[0m
[2;32m[][0m is [2;32mOptional[0m

{usage_line}
{underline_line}[0m
```
Please **check the command** and *try again*.""",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Tip: use keyboard to type {PREFIX}help {ctx.invoked_with} to let me explain the command for you! 😼")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1261693021628530769/1361637770174660699/convert.gif?ex=67ff7b7e&is=67fe29fe&hm=1021ea6333ed2bee4184951627a1da9600ed3684da1c56530378cd41358c8418&")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1260474179359215717/1355148212276691228/cat-funny.gif?ex=67ff9a9f&is=67fe491f&hm=769511cf5fe0aaae67d25208263880bb605d48d8a6f91abfe378dddc0cf8519c&")
            await ctx.send(embed=embed)
            
        # ---------------------------------------------------------------------------- #
        #                              MissingPermissions                              #
        # ---------------------------------------------------------------------------- #
        elif isinstance(error, commands.MissingPermissions):
            self.Logger.warning(f'[grey70]{ctx.author.name}[/] '
                                f'- MISSING PERMISSIONS in [bold underline link=https://discordapp.com/channels/{ctx.message.guild.id}/{ctx.channel.id}/{ctx.message.id}]#{ctx.channel.name}[/bold underline link]: '
                                f'[grey50]{PREFIX}{ctx.invoked_with}[/]')
            
            embed = discord.Embed(
                description=f"""# {self.Emojis.SecurityCat} ・ Missing Permissions
{self.Emojis.CatBlehCUTE}*Bleh*~~.. You don't have *enough permissions* to use this command!
These is required permissions:
- {'\n- '.join(error.missing_permissions)}

Please check your **permissions / roles** and try again.""",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Tip: type {PREFIX}help {ctx.invoked_with} to see what permissions is required to use.")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1222666666308010124/1280641900101111880/attachment.gif?ex=67ff7976&is=67fe27f6&hm=b8a9f926b12d50a3fccf3be95563ff2e7733be44d21a0de6324c02403fca7774&")
            
            await ctx.send(embed=embed)
            
        # ---------------------------------------------------------------------------- #
        #                               CommandOnCooldown                              #
        # ---------------------------------------------------------------------------- #
        elif isinstance(error, commands.CommandOnCooldown):
            cooldown_time: datetime.datetime = datetime.datetime.now() + datetime.timedelta(0, error.retry_after)
            cooldown_time = int(cooldown_time.timestamp())
            self.Logger.warning(f'[grey70]{ctx.author.name}[/] '
                                f'- COMMAND ON COOLDOWN in [bold underline link=https://discordapp.com/channels/{ctx.message.guild.id}/{ctx.channel.id}/{ctx.message.id}]#{ctx.channel.name}[/bold underline link]: '
                                f'[grey50]{PREFIX}{ctx.invoked_with} ({error.retry_after:.2f} seconds)[/grey50]')
            
            embed = discord.Embed(
                description=f"""# {self.Emojis.SecurityCat} ・ Command On Cooldown
{self.Emojis.CatEatingChips}*crunch* *crunch* *crunch*...
Slow down hooman! You are typing too fast (i really *wow* on your typing speed)
-# You can use this command till <t:{cooldown_time}:F>.""",
                color=discord.Color.light_gray()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1260474179359215717/1356666959563067595/surprise-cat.gif?ex=67ff3250&is=67fde0d0&hm=301f874365de5230068e238975362fba5b1f0f957db48faebdbf4c07e086eb26&")
            await ctx.send(embed=embed, delete_after=error.retry_after)
            
        # ---------------------------------------------------------------------------- #
        #                             BotMissingPermissions                            #
        # ---------------------------------------------------------------------------- #
        elif isinstance(error, commands.BotMissingPermissions):
            self.Logger.warning(f'[grey70]{ctx.author.name}[/] '
                                f'- BOT MISSING PERMISSIONS in [bold underline link=https://discordapp.com/channels/{ctx.message.guild.id}/{ctx.channel.id}/{ctx.message.id}]#{ctx.channel.name}[/bold underline link]: '
                                f'[grey50]{', '.join(error.missing_permissions)} ({PREFIX}{ctx.invoked_with})[/grey50]')
            
            embed = discord.Embed(
                description=f"""# {self.Emojis.SecurityCat} ・ MEOW Missing Permissions
## {self.Emojis.JustWokeUp}<- this is me.
Sorry hooman, I *meown't* even have enough permissions to execute this command!
Please recheck my permissions and try again.""",
                color=discord.Color.red()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1218440992651218959/1255879183931019294/image_2024-06-27_213452161.gif?ex=67ff0962&is=67fdb7e2&hm=6d8018ad014b3ec4df908d49c120df3961828693a144eef020917cd8cc90aadd&")
            await ctx.send(embed=embed)
            
        # ---------------------------------------------------------------------------- #
        #                                 Unknown Error                                #
        # ---------------------------------------------------------------------------- #
        else:
            embed = discord.Embed(
                description=f"""# {self.Emojis.SecurityCat} ・ Wait wait wait wait...
Hi, I am **Security Cat**, 
I might be **very _silly_ and _confused_** right now {self.Emojis.CatScare},
I just got an **error** and I don't even *meow* what **actually it is**...

## Error:
- {error}

**Please report this error to my owner, and I will try to fix it as soon as possible!**""",
                color=discord.Color.red()
            )
            embed.set_footer(text="traleleo tralala")
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/914508501697576990/1314542204722741248/caption.gif?width=778&height=671&ex=6804cf54&is=68037dd4&hm=3962bf30d533218aac86dd56ae52ad7100225f05de2c5a76016dd7103c071b7f&")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1152219170725974036/1344559323518599241/convert.gif?ex=68049673&is=680344f3&hm=04144ffe112bc1e2a239f783e037d0e7c473cff6416275d51b1a2c8159446b8d&")
            await ctx.send(embed=embed)
            try:
                raise error
            except Exception as e:
                self.Logger.exception(f'[grey70]{ctx.author.name}[/] '
                                f'- [red]UNKNOWN ERROR[/] in [bold underline link=https://discordapp.com/channels/{ctx.message.guild.id}/{ctx.channel.id}/{ctx.message.id}]#{ctx.channel.name}[/bold underline link]: '
                                f'[grey50]{PREFIX}{ctx.invoked_with}[/grey50]\n[bright_red]{e}[/]')


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                               >meow                                              #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    # --------------------------------------- btw, this is ping -------------------------------------- #
    @BetterCommand(
        name="meow",
        description="Meow meo meow, MEOW, meow meow meo meo meo..w",
        brief="Meow meow meow",
        help="""Meow meo meow meow, meow meow meow. Meow meow meow **meow meow**.
Meow meow meo meo meo meow *meow*, meow meow meow meo?
Meow meow meo meo meo meo meow! <3""",
        usage=f"**Just use** `{PREFIX}meow` to  *meow meow meow*.",
        aliases=["meowmeowmeow"],
    )
    async def meow(self, ctx: commands.Context):
        embed = discord.Embed(
            description=f"""# {self.Emojis.random()} Meow meow meow meow meow meow
# {self.Emojis.random(10)} 
Meow meow meow meow! Meo meo meo mèo meow~ 
*Meooooow* meow meow **meo meo**! *Meow meow* meo mèo meo.
Meo meo meow meow meow? **MEOW MEOW**! Meo meo mèo...
Meow meow meo meo meow meow! Meo meo mèo meow meow~""",
            color=discord.Color.green()
        )
        embed.url = "https://online.fliphtml5.com/foaxv/zvfb/#isOldNeat"
        embed.add_field(name="Latency", value=f"`{self.bot.latency * 1000:.2f}ms`", inline=True)
        embed.add_field(name="RAM Usage", value=f"`{psutil.Process().memory_info().rss / 1024 / 1024:.2f}MB`", inline=True)
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else "https://cdn.discordapp.com/attachments/1258599258345443441/1264950931032637520/uDpr09A.gif?ex=680af21b&is=6809a09b&hm=18dd712186bed4d9c9831ab46c9a04a6ebec8844669e5f07a9d852b8d363136d&")
        embed.set_image(url="https://preview.redd.it/uzyft60tser11.jpg?width=1080&crop=smart&auto=webp&s=7a6a169625dff3efba42c8643e5576ed38c9bcf3")

        await ctx.send(embed=embed)


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                              >random                                             #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    @BetterCommand(
        name="howlove",
        description="Check how much some one love silly cats is",
        brief="Check how much some one love silly cats",
        help="""How much you love **silly _cats_**?
**I will calculate it for you!**
""",
        usage=f"""Well well well, you can use it like this:
{HelpFormat(f"{PREFIX}howlove", Optional=["member"])}
-# You can use it without any argument to check how much you love silly cats.""",
    )
    async def howlove(self, ctx: commands.Context,*, member: discord.Member = None, ephemeral: bool = False):
        """
        Calculate how much a member loves cats.
        
        Args:
            ctx (commands.Context): The context of the command.
            member (discord.Member, optional): The member to calculate the love for. Defaults to the author.
            ephemeral (bool, optional): Please send me secretly (only me can see it). (Default: False, Optional)
        """
        if member is None:
            member = ctx.author
        
        if member == ctx.guild.me:
            embed = discord.Embed(
                description=f"""# {self.Emojis.random()} Meow meow meo...
## You don't need to check me, I'm already a cat lover!
-# I love cats so much! <3""",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Meow meow meo~, I love you more than you know!")
            embed.set_thumbnail(url=member.avatar.url if member.avatar else "https://c.tenor.com/62O0lwQIiwwAAAAd/tenor.gif")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1252365615281340498/1305546137427640320/togif.gif?ex=680af957&is=6809a7d7&hm=b9b078b340a3da54037c0c715505a092d6b6dd9eadd7d907018f1f693e9263b3&")
            await ctx.send(embed=embed, ephemeral=ephemeral)
            return
        
        embed = discord.Embed(
            title=f"",
            description=f"""# {self.Emojis.random()} Calculating Love for Silly Cats
## Let me check how much **{member.display_name}** loves cats...""",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Well well well, I'm not sure if this is correct, but I'll try my best!")
        embed.set_thumbnail(url=member.avatar.url if member.avatar else "https://c.tenor.com/62O0lwQIiwwAAAAd/tenor.gif")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1252365615281340498/1305546137427640320/togif.gif?ex=680af957&is=6809a7d7&hm=b9b078b340a3da54037c0c715505a092d6b6dd9eadd7d907018f1f693e9263b3&")
        msg = await ctx.send(embed=embed, ephemeral=ephemeral)
        
        steps = [
            self.Emojis.random() + "** Analyzing cat photos in gallery...**",
            self.Emojis.random() + "** Checking kitty treat purchases...**", 
            self.Emojis.random() + "** Scanning for cat videos watched...**",
            self.Emojis.random() + "** Measuring heart rate near cats...**"
        ]
        
        for step in steps:
            await asyncio.sleep(rd.randint(1, 4))
            embed.description = f"""# {self.Emojis.random()} Calculating Love for Silly Cats      
## {step}"""
            await msg.edit(embed=embed)
        
        await asyncio.sleep(2)
        love_percent = rd.randint(0, 100)
        
        # Determine love level and message
        if love_percent >= 80:
            level = "Ultimate Cat Lover! 😻"
            color = discord.Color.red()
        elif love_percent >= 60:
            level = "Cat Enthusiast! 😺"
            color = discord.Color.blue() 
        elif love_percent >= 40:
            level = "Cat Friend 🐱"
            color = discord.Color.green()
        else:
            level = "Still Learning to Love Cats 😿"
            color = discord.Color.dark_gray()
            
        hearts = '❤️' * (love_percent // 10)
        empty_hearts = '🖤' * ((100 - love_percent) // 10)
        
        embed.color = color
        embed.description = f"""# {self.Emojis.random()} Love Calculator Results
### {level}

**{member.name}**'s Love for Cats: **{love_percent}%**
{hearts}{empty_hearts}

-# *The more you love cats, the more they love you back!* {self.Emojis.random()}"""
        
        await msg.edit(embed=embed)
    


        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))