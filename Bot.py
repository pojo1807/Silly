import datetime
import discord
from discord.ext import commands
from discord.ext.commands import Cog, Command

import sys
import dotenv
import os
import platform
import time
import json
import argparse
import re
from typing import Any, Callable, Dict, List, Optional

import logging
from rich.console import Console

from Utils.Globals import PREFIX
from Utils.Helper import Emojis
from Utils.Utils import *


COMMANDS_PATH = os.path.join(os.getcwd(), "Cogs")
LOG_FILENAME = "Silly.log"

parser = argparse.ArgumentParser()
parser.add_argument(
    '--sync',
    nargs='?',
    const="all",
    default=None,
    metavar='GUILD_ID',
    help="Sync all commands to the guild. use \"--sync <GUILD_ID>\" to sync to a specific guild, or \"--sync\" to sync to all guilds."
)

parser.add_argument(
    '--debug',
    action="store_true",
    help="Enable debug mode. This will enable debug logging and set the logging level to DEBUG."
)

args = parser.parse_args()



class Silly(commands.Bot):
    async def load_all_extensions(self) -> None:
        """Load all extensions from the Cogs folder.
        """
        self.Logger.info(f"Loading commands from {COMMANDS_PATH}")
        for filename in os.listdir(COMMANDS_PATH):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    await self.load_extension(f"Cogs.{filename[:-3]}")
                    self.Logger.info(f"LOADED command {filename}")
                except Exception as e:
                    self.Logger.error(f"FAILED to load command {filename}: {e}")

    class Help(commands.HelpCommand):
        def __init__(self, **options):
            self.Emojis = Emojis
            super().__init__(**options)
            
            self.command_attrs["description"] = "Need help, *hooman*? I can **smeowll** it!!\nI will **explain everything** I understand for **you**!"
            self.command_attrs["brief"] = "Let the **silliest cat** help you"
            self.command_attrs["aliases"] = ["meow, wheresisthesilliestcat", "pleasehelpimtoosilly"]
            
        
        """def get_command_signature(self, command):
            return f"{self.Helpers.Prefix}{command.qualified_name} {command.signature}"""
            
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ >help ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
        async def send_bot_help(self, mapping: Dict[Optional[Cog], List[Command]]):
            ctx = self.context
            embed = discord.Embed(
                description=f"""# {self.Emojis.random()} ・ Meo Help Center
**Meow!, I am _Silly_.**
I am here to help you with your *silly* needs.
""",
                color=discord.Color.green()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362386665569779803/Silly_6.gif?ex=680234f4&is=6800e374&hm=c82b1ace8d364a1b641a17f1b7b08b548e566af3f38e3c8f537464d44e82db3d&")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362385462278225971/SillyCat.png?ex=680233d6&is=6800e256&hm=59610ec0e8157398191d3063463ff8deae66618787058c0e47318982c9a3775e&")
            embed.add_field(name="Prefix", value=f"`{PREFIX}`", inline=False)
            for cog, commands_list in mapping.items():
                filtered = await self.filter_commands(commands_list, sort=True) # Filter commands and sort that shit
                if filtered:
                    Category = f"{cog.Emoji}   {cog.qualified_name}" if cog else f"{self.Emojis.UIA_Spinning}   Other (No Category)"
                    embed.description += f"\n# {Category}\n"
                    for cmdidx, cmd in enumerate(filtered):
                        
                        CommandName = cmd.name
                        CommandDescription = cmd.brief
                        
                        # bro its chatgpt icl but i wrote comments
                        (RequiredParams, OptionalParams) = ([f"[{param.name}]" for param in cmd.clean_params.values() # Get clean params (filtered the self and ctx)
                                          if param.default is param.empty # Check if param has a default value, if not, it's required
                                          and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY) # Check if param is positional or keyword only
                                          ],
                                                            
                                          [f"<{param.name}>" for param in cmd.clean_params.values() # Get clean params (filtered the self and ctx)
                                          if param.default is not param.empty # Check if param has a default value, if yes, it's mot required
                                          and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY) # Check if param is positional or keyword only
                                          ] # Get optional params
                        )
                        
                        embed.description += f"""### {cmdidx+1}. {CommandName}{f" `{' '.join(RequiredParams)}`" if RequiredParams else ''}{f" `{' '.join(OptionalParams)}`" if OptionalParams else ''}{f"\n-#  Aliases: **{'**, **'.join(cmd.aliases)}**" if cmd.aliases else ''}
> {repr(CommandDescription).strip('"').strip("'")}   
""" # repr to make the "    - " work
            await ctx.send(embed=embed)
            
    
        # ------------------------------ >help <command> ----------------------------- #
        async def send_command_help(self, command: commands.Command):
            ctx = self.context
            embed = discord.Embed(
                description=f"""# {self.Emojis.random()} ・ Meo Help Center
**Meow!, I am _Silly_.**
I am here to help you with your **_silly_ needs**.

**Help for `{command.name}` in {command.cog.Emoji} __{command.cog_name or "Other"}__**

# {self.Emojis.NerdCat}   Description
{command.description}

# {self.Emojis.JustWokeUp}   Usage
{command.usage}

# {self.Emojis.InsaneArhh}   Aliases
{', '.join(command.aliases) if command.aliases else f'No aliases... {self.Emojis.UIA_Spinning}'}
""",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url="https://c.tenor.com/KO80NCIjQAUAAAAd/tenor.gif")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362386665569779803/Silly_6.gif?ex=680234f4&is=6800e374&hm=c82b1ace8d364a1b641a17f1b7b08b548e566af3f38e3c8f537464d44e82db3d&")
            await ctx.send(embed=embed)
        
        # ------------------------------ >help <category> ----------------------------- #

        async def send_cog_help(self, group: commands.Cog):
            ctx = self.context
            embed = discord.Embed(
                description=f"""# {self.Emojis.random()} ・ Meo Help Center
**Meow!, I am _Silly_.**
I am here to help you with your **_silly_ needs**.

# {group.Emoji} __{group.qualified_name}__
""",
                color=discord.Color.green()
            )
            
            #logging.getLogger("silly").info(f"Sending group help for {group.qualified_name}")
            filtered = await self.filter_commands(group.get_commands(), sort=True)
            for cmd in filtered:
                CommandName = cmd.name
                CommandDescription = cmd.brief

                (RequiredParams, OptionalParams) = ([f"[{param.name}]" for param in cmd.clean_params.values() # Get clean params (filtered the self and ctx)
                                    if param.default is param.empty # Check if param has a default value, if not, it's required
                                    and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY) # Check if param is positional or keyword only
                                    ],
                                                    
                                    [f"<{param.name}>" for param in cmd.clean_params.values() # Get clean params (filtered the self and ctx)
                                    if param.default is not param.empty # Check if param has a default value, if yes, it's mot required
                                    and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY) # Check if param is positional or keyword only
                                    ] # Get optional params
                )
                
                embed.description += f"""- **{CommandName}{f" `{' '.join(RequiredParams)}`" if RequiredParams else ''}{f" `{' '.join(OptionalParams)}`" if OptionalParams else ''}**{f"\n-#  Aliases: **{'**, **'.join(cmd.aliases)}**" if cmd.aliases else ''}
  - {repr(CommandDescription).strip('"').strip("'")}
  
"""
            embed.set_thumbnail(url="https://c.tenor.com/KO80NCIjQAUAAAAd/tenor.gif")
            embed.set_image(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362386665569779803/Silly_6.gif?ex=680234f4&is=6800e374&hm=c82b1ace8d364a1b641a17f1b7b08b548e566af3f38e3c8f537464d44e82db3d&")
            await ctx.send(embed=embed)
            
            
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ERROR WHEN COMMAND NOT FOUND ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
        async def send_error_message(self, error): 
            ctx = self.context
            
            embed = discord.Embed(
                description=f"""# {self.Emojis.random()} ・ Meo Help Center
**Meow!, I am _Silly_.**
I am here to help you with your **_silly_ needs**.
### {self.Emojis.CatScare} ・ Error
- {error}

**Please use `{PREFIX}help` to get help.**
-# *im so proud*
""",    
                color=discord.Colour.red()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362386665569779803/Silly_6.gif?ex=680234f4&is=6800e374&hm=c82b1ace8d364a1b641a17f1b7b08b548e566af3f38e3c8f537464d44e82db3d&")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1218440992651218959/1255879183931019294/image_2024-06-27_213452161.gif?ex=6801ac62&is=68005ae2&hm=e4bd704f6e03141cb1ff88f306e285654f41de4c45f666f0d79969317e17ce41&")
            await ctx.send(embed=embed, delete_after=15)
            
        async def command_callback(self, ctx, *, command=None):
            """The actual implementation of the help command."""
            if command is None:
                return await self.send_bot_help(self.get_bot_mapping())
            
            # Check if it's a cog name (case-insensitive)
            command_lower = command.lower()
            for cog in ctx.bot.cogs.values():
                if cog.qualified_name.lower() == command_lower:
                    return await self.send_cog_help(cog)
            
            # Check if it's a command
            cmd = ctx.bot.get_command(command_lower)
            if cmd is not None:
                return await self.send_command_help(cmd)
            
            # If we get here, the command wasn't found
            return await self.send_error_message(commands.CommandNotFound(f"**Uh oh, the command named `{command}` was not found!**"))
            
    
    def __init__(self) -> None:
        # Init console n Logger
        self.Console = Console()
        
        self.Logger = logging.getLogger("silly")
        
        self.Console.clear()
        self.Console.set_window_title(f"Silly - Running on {platform.system()} {platform.release()}")
        self.Console.print("""
⣿⡏⠙⠛⠻⢿⣿⣿⣟⣿⣿⣿⣛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣿⣿⣿⣿⠿⠋⠉⣟⡟⣟⣛⣿⣿
⣿⣹⠀⠀⠀⠀⠈⠙⠻⢿⣿⣿⣧⣛⢿⣿⡿⠿⣟⣋⣿⡿⣟⡿⣿⣿⣿⡿⢿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠉⠀⠀⠀⣞⡟⣜⢳⣿⣿
⣽⣿⣷⡀⠀⠀⠀⠀⠀⠀⠉⠻⠿⢿⣿⣿⣿⡿⣿⡿⣿⣋⣛⡿⢯⣽⣯⣿⣯⣿⣿⠿⠟⠿⠿⣿⣿⠟⠋⠀⠀⠀⠀⣰⣿⣯⡿⣿⣿⣿
⣯⠟⣷⡿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠋⠁⠀⠀⠀⠀⠀⠈⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿
⣗⢫⢽⣧⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿
⣬⡿⣿⢿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣻⣿⣿⣿⣿⣿
⣿⣿⣻⢷⡍⣿⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣄⣀⣀⣀⠀⠀⠈⢿⣿⡏⣿⣿⣿
⡫⡟⢿⡝⢿⣿⠀⠀⠀⠀⠀⠛⠿⣯⣭⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣶⣿⣿⣿⡿⠿⠟⠋⠙⠃⠀⠀⠿⢿⣿⢿⣿⣿
⣿⡛⣽⣷⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠈⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡘⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢻⣿⣿⣿
⣻⡿⢻⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⠀⠠⣴⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿
⣿⡿⣷⣿⣇⠀⠀⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣦⣄⡉⠉⠉⠉⣱⣶⠟⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⢀⠀⠤⡀⢸⢲⣶⣿⣿
⣻⡿⢿⣿⣿⡄⠀⠀⠀⢰⠦⢤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⡉⢴⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⢘⡛⡿⢿⣿⡿⣿
⢹⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⢀⣤⡤⠤⠤⠀⠀⠀⢀⡀⠀⠀⠈⢻⣿⠇⠀⠀⣀⣀⣤⡤⠶⠾⠛⠛⠿⣭⣍⡉⠙⢻⢿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣏⣿⣿⡀⠀⠀⠐⠋⠁⠉⠱⠶⠶⣶⣾⣷⣤⣉⣉⣩⣴⣿⣿⣦⣤⣤⣤⣤⣤⡖⠒⠒⠒⢦⣄⠀⠉⣙⠷⣷⣿⣦⣬⣛⣻⡿
⣿⣿⣿⣭⡿⣷⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠽⣿⣿⠟⠋⠉⠉⠉⠉⠉⠉⠉⢹⣿⠀⠀⠀⢀⠀⠉⠳⣦⡈⢹⡲⣿⣿⣿⣿⣿⣿
⣿⢟⣻⣋⣻⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠙⢷⣰⣿⡻⣿⣿⣿⣿
⢼⣮⣿⣿⠟⣹⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡇⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⣸⣷⠀⠀⠀⠀⠀⠀⠘⢦⠈⠙⣿⣿⣷⣝⢿⣿
⣿⣿⢟⣷⠾⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠙⢣⡟⣄⠀⢀⣴⣿⠃⠀⠀⠀⠀⠀⠀⠀⠈⠃⢸⠻⣿⣿⣿⣷⣬
⠟⣿⡾⣋⣼⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠓⠀⠀⠀⣀⣿⠁⢙⢆⢸⣧⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿
⡾⣟⣿⡟⣽⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠿⠿⢿⣿⣿⡿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿
⢷⢛⠹⡗⡻⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿
⢷⣧⣎⠯⠞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿
⣈⡛⠋⠯⠞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿

Made with [bright_red]<3[/] by [royal_blue1]fat0426[/]
[gray35]https://github.com/duckfatscooby
Python     v{}
Discord.py v{}[/]""".format(platform.python_version(), discord.__version__))
        
        self.Console.rule("Logs", style="bright_black")
            
        self.Emojis = Emojis
        
        super().__init__(intents=discord.Intents.all(), # i dont know but the "all" works instead of "default"
                         #help_command=None, # remove the default help command
                         command_prefix=PREFIX,
                         help_command=Silly.Help()
                         )
        
    async def on_ready(self) -> None:
        """This one called when the bot is ready (after setup_hook).
        """
        self.Logger.info("Silly is ready!")
        self.Logger.info(
f"Logged in as \"{self.user.name}#{self.user.discriminator}\" [gray35]({self.user.id})[/gray35]\nInvite via [blink]https://discord.com/oauth2/authorize?client_id={self.user.id}&permissions=8&integration_type=0&scope=bot[/blink]"
        )
        # Set status
        await self.change_presence(activity=discord.Game(name="Silly cats :P")) # static for now
        
        
        
        if self.Emojis._emojis is None:
            self.Logger.warning(f"No emojis found! It may cause response issues.\nPlease every single emoji in \"_Emojis\" folder in https://discord.com/developers/applications/{self.user.id}/emojis")
        
    async def setup_hook(self):
        """This one called first when the bot is ready.
        """
        await self.Emojis.Init(self)
        # Load all commands
        await self.load_all_extensions()
        
        # Sync commands if --sync is provided
        if args.sync != None:
            self.Logger.info(f"Syncing commands... ({args.sync})")
            if args.sync == "all":
                try:
                    sync_commands = await self.tree.sync()
                    
                    self.Logger.info(f"SYNCED {len(sync_commands)} commands!")
                except Exception as e:
                    self.Logger.error(f"FAILED to sync commands: {e}")
            else:
                guild = discord.Object(id=int(args.sync))
                try:
                    sync_commands = await self.tree.sync(guild=guild)
                    self.Logger.info(f"SYNCED {len(sync_commands)} commands to {guild.name} ({guild.id})")
                except Exception as e:
                    self.Logger.error(f"FAILED to sync commands to {guild.name} ({guild.id}): {e}")
                    
        return await super().setup_hook()
    

    #Error handlers
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
            self.Logger.error(f'[grey70]{ctx.author.name}[/] '
                                f'- UNKNOWN ERROR in [bold underline link=https://discordapp.com/channels/{ctx.message.guild.id}/{ctx.channel.id}/{ctx.message.id}]#{ctx.channel.name}[/bold underline link]: '
                                f'[grey50]{PREFIX}{ctx.invoked_with}[/grey50]\n[bright_red]{error}[/]')
            
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
            self.Logger.exception(f'[bright_red]{error}[/]')
            await ctx.send(embed=embed)

        



if __name__ == "__main__":
    setup_rich_logging(LOG_FILENAME=LOG_FILENAME, debug=args.debug)
    
    #Add new line for log file
    with open(LOG_FILENAME, "a") as f:
        f.write("\n\n\n")
        f.write(f"Started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    dotenv.load_dotenv()

    TOKEN = os.getenv("TOKEN")

    if TOKEN is None or TOKEN == "":
        print("Error: TOKEN environment variable not set.")
        sys.exit(1)
    

    client = Silly()
    

    client.run(TOKEN)