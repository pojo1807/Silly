import discord
from discord.ext import commands
from discord.ext.commands import Cog, Command
import sys
import dotenv
import os
import platform
import time
import argparse
from typing import Dict, List, Optional

import logging
from rich.console import Console

from Utils.Globals import PREFIX
from Cogs.General import General
from Utils.Helper import Emojis, INI, get_required_permissions
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
            
            
            # i dont know why but help command doesnt support customize help coommand
            # so i have to do this
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
            embed.add_field(name="Current Prefix", value=f"`{PREFIX}`", inline=False)
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
""" 
            await ctx.send(embed=embed)
            
    
        # ------------------------------ >help <command> ----------------------------- #
        async def send_command_help(self, command: commands.Command):
            ctx = self.context
            
            # Get required permissions
            required_permissions = get_required_permissions(command)
            
            permissions_text = (
                "\n".join([f"- `{perm.replace('_', ' ').title()}`" for perm in required_permissions])
                if required_permissions
                else f"{self.Emojis.UIA_Spinning * 3}"
            )
            
            embed = discord.Embed(
                description=f"""# {self.Emojis.random()} ・ Meo Help Center
**Meow!, I am _Silly_.**
I am here to help you with your **_silly_ needs**.

**Help for `{command.name}` in {command.cog.Emoji} __{command.cog_name or "Other"}__**

# {self.Emojis.NerdCat}   Description
{command.description}

# {self.Emojis.JustWokeUp}   Usage
{command.usage}
# {self.Emojis.SecurityCat}   Required Permissions
{permissions_text}

# {self.Emojis.InsaneArhh}   Aliases
{', '.join(command.aliases) if command.aliases else f'{self.Emojis.UIA_Spinning}'}
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
            
        # ---------------------------------------------------------------------------- #
        #                       REPLACED COMMAND CALLBACK                              #
        # ---------------------------------------------------------------------------- #
        async def command_callback(self, ctx, *, command=None):
            """The actual implementation of the help command."""
            if command is None:
                return await self.send_bot_help(self.get_bot_mapping())
            
            # Check if it's a cog name (case-insensitive)
            command_lower = command.lower()
            for cog in ctx.bot.cogs.values():
                if cog.qualified_name.lower() == command_lower:
                    return await self.send_cog_help(cog)
            
            # Check if it's a command (case-insensitive)
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
        self.Console.print(rf"""
                           
            *   [bold]  ,MMM8&&&.[/]            *
                  [bold]MMMM88&&&&&[/]    .
                 [bold]MMMM88&&&&&&&[/]
     *           [bold]MMM88&&&&&&&&[/]
                 [bold]MMM88&&&&&&&&[/]
                 [bold]'MMM88&&&&&&'[/]
                   [bold]'MMM8&&&'[/]      *    
          |\___/|     /\___/\
          )     (     )    ~( .              '
         =\     /=   =\~    /=
           )===(       ) ~ (
          /     \     /     \
          |     |     ) ~   (
         /       \   /     ~ \
         \       /   \~     ~/
  jgs_/\_/\__  _/_/\_/\__~__/_/\_/\_/\_/\_/\_
  |  |  |  |( (  |  |  | ))  |  |  |  |  |  |
  |  |  |  | ) ) |  |  |//|  |  |  |  |  |  |
  |  |  |  |(_(  |  |  (( |  |  |  |  |  |  |
  |  |  |  |  |  |  |  |\)|  |  |  |  |  |  |
  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
  
  
Made with [bright_red]<3[/] by [royal_blue1]fat0426[/] on [cornflower_blue]Discord[/]
[gray35]https://github.com/pojo1807
Python     v{platform.python_version()}
Discord.py v{discord.__version__}[/]""", highlight=False)
        
        self.Console.rule("Logs", style="bright_black")
            
        self.Emojis = Emojis
        
        
        super().__init__(intents=discord.Intents.all(), # i dont know but the "all" works instead of "default"
                         #help_command=None, # remove the default help command
                         command_prefix=PREFIX
                         )
        
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                             ON READY                                             #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    async def on_ready(self) -> None:
        """This one called when the bot is readsy (after setup_hook).
        """
        self.Logger.info("Silly is ready!")
        self.Logger.info(
f"Logged in as \"{self.user.name}#{self.user.discriminator}\" [gray35]({self.user.id})[/gray35]\nInvite via [blink]https://discord.com/oauth2/authorize?client_id={self.user.id}&permissions=8&integration_type=0&scope=bot[/blink]"
        )
        # Set status
        await self.change_presence(activity=discord.Game(name="with my hooman")) # static for now
        
        self.help_command = self.Help()
        
        if self.Emojis._emojis is None:
            self.Logger.warning(f"No emojis found! It may cause response issues.\nPlease add every single emoji in \"_Emojis\" folder in https://discord.com/developers/applications/{self.user.id}/emojis")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                            SETUP HOOK                                            #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
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
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                       ADDITIONAL FUNCTIONS                                       #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #

    

        



if __name__ == "__main__":
    setup_rich_logging(LOG_FILENAME=LOG_FILENAME, debug=args.debug)
    
    #Check if Auto_Update_Discord_Py is True
    if INI.getboolean("Startup_Settings", "Auto_Update_Discord_Py"):
        #Upgrade discord.py at first
        print("Upgrading discord.py to keep it up to date...")
        try:
            os.system("pip install --upgrade discord.py >nul 2>&1")
        except Exception as e:
            print(f"Error: {e}")
    
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