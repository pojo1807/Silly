import discord
from discord.ext import commands
import sys
import dotenv
import os
import platform
import time
import argparse

import logging
from rich.console import Console

from Utils.Globals import PREFIX

from Utils.Helper import Emojis, INI
from Utils.Utils import *

COMMAND_NAMES = [ # i change from auto get to this because i want to change the order of the categories
    "General",
    "Moderation",
    "Fun",
    "Utilities",
    #... i will add more here later ;)
]
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
    __version__ = "0.0.6"
    async def load_all_extensions(self) -> None:
        """Load all extensions from the Cogs folder.
        """
        self.Logger.info(f"Loading commands from \"Cogs\" folder")
        for filename in COMMAND_NAMES:
            try:
                await self.load_extension(f"Cogs.{filename}")
                self.Logger.info(f"LOADED command {filename}")
            except Exception as e:
                self.Logger.exception(f"FAILED to load command {filename}")

    
    def __init__(self) -> None:
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
[gray35]https://github.com/pojo1807 [Current version: {self.__version__}]
Python     v{platform.python_version()}
Discord.py v{discord.__version__}[/]""", highlight=False)
        
        self.Console.rule("Logs", style="bright_black")
            
        self.Emojis = Emojis
        
        super().__init__(intents=discord.Intents.all(), # i dont know but the "all" works instead of "default"
                         help_command=None,
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
f"Logged in as \"{self.user.name}#{self.user.discriminator}\" [gray35]({self.user.id})[/gray35]"
        )
        # Set status
        await self.change_presence(activity=discord.Game(name="with my hooman")) # static for now
        
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
                    
                    # test slash command style
                    for cmd in sync_commands:
                        #self.Logger.debug(f"cmd id: {cmd.id}")
                        # save the id to the INI file
                        # neu lan sau khong sync thi co the lay id tu file INI
                        INI.set(f"Slash_Commands", cmd.name, str(cmd.id))
                    with open("Settings.ini", "w") as f:
                        INI.write(f)
                    
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