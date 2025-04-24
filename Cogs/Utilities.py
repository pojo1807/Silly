import logging
import platform
from typing import Dict, List, Optional
from Cogs.__init__ import BetterCommand
from discord.ext import commands
from discord import app_commands
from Utils.Helper import Emojis, get_required_permissions, INI
from Utils.Globals import PREFIX
import discord
import psutil

logger = logging.getLogger("silly") 

class Help(commands.HelpCommand):
    def __init__(self, **options):
        self.Emojis = Emojis
        options["command_attrs"] = {
            "name": "_help",  # chnage to _help to remove duplicate help command, will use help function to pass
            "hidden": True    # hide default help command
        }
        super().__init__(**options)
    
        
    
    """def get_command_signature(self, command):
        return f"{self.Helpers.Prefix}{command.qualified_name} {command.signature}"""
        
    async def smart_send(self, ctx, *args, **kwargs):
        if isinstance(ctx, discord.Interaction):
            if not ctx.response.is_done():
                await ctx.response.send_message(*args, **kwargs)
            else:
                await ctx.followup.send(*args, **kwargs)
        elif hasattr(ctx, "send"):
            await ctx.send(*args, **kwargs)
        else:
            logger.error(f"Invalid context type: {type(ctx)}")
            raise TypeError(f"ctx must be Context or Interaction, got {type(ctx)}")
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                               >help                                              #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    async def send_bot_help(self, mapping: Dict[Optional[commands.Cog], List[commands.Command]], ephemeral: bool = False):
        ctx = self.context
        logger.debug(f"ctx: {ctx}")
        embed = discord.Embed(
            description=f"""# {self.Emojis.random()} ・ Meo Help Center
Welcome to **Silly's** help menu! I'm here to assist you with all your **_silly_ needs.**

-# Use `{PREFIX}help [command]` or `/help [command]` for detailed help on a specific command.
-# Use `{PREFIX}help [category]` or `/help [category]` to see all commands in a category.""",
            color=discord.Color.green()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362386665569779803/Silly_6.gif?ex=680234f4&is=6800e374&hm=c82b1ace8d364a1b641a17f1b7b08b548e566af3f38e3c8f537464d44e82db3d&")
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else ctx.author.avatar.url if ctx.author.avatar else "https://c.tenor.com/KO80NCIjQAUAAAAd/tenor.gif")
        embed.add_field(name="Current Prefix", value=f"`{PREFIX}`", inline=False)
        embed.set_footer(text=f"Hint: < > = Optional argument  •  [ ] = Required argument")
        for cog, commands_list in mapping.items():
            filtered = await self.filter_commands(commands_list, sort=True) # Filter commands and sort that shit
            if filtered:
                Category = f"{cog.Emoji}   {cog.qualified_name}" if cog else f"{self.Emojis.UIA_Spinning}   Other (No Category)"
                embed.description += f"\n# {Category}\n"
                for cmdidx, cmd in enumerate(filtered):
                    if cmd.hidden and not self.show_hidden:
                        continue
                    
                    CommandName = cmd.name
                    CommandDescription = cmd.brief
                    
    
                    # Get Command ID from INI file i should sync for every new command
                    slash_cmd_id = INI.get('Slash_Commands', cmd.name, fallback=None)
                    #logger.debug(f"no sync: slash_cmd_id: {slash_cmd_id}")
                    
                    if slash_cmd_id:
                        CommandName += f" (</{cmd.name}:{slash_cmd_id}>)"
                    
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
        logger.debug(f"embed: {embed}")
        logger.debug(f"ephemeral: {ephemeral}")
        await self.smart_send(ctx, embed=embed, ephemeral=ephemeral)
        

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                          >help COMMAND                                           #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    async def send_command_help(self, command: commands.Command, ephemeral: bool = False):
        ctx = self.context
        
        # Get required permissions
        required_permissions = get_required_permissions(command)
        
        permissions_text = (
            "\n".join([f"- `{perm.replace('_', ' ').title()}`" for perm in required_permissions])
            if required_permissions
            else f"-# {self.Emojis.UIA_Spinning}"
        )
        
        embed = discord.Embed(
            description=f"""# {self.Emojis.random()} ・ Meo Help Center
Welcome to **Silly's** help menu! I'm here to assist you with all your **_silly_ needs.** {self.Emojis.CatScare}

## {command.cog.Emoji} Command: `{command.name}`
> Category: __{command.cog_name or "Other"}__

# {self.Emojis.NerdCat} Description
{command.help}

# {self.Emojis.JustWokeUp}   Usage
{command.usage}

# {self.Emojis.SecurityCat}   Required Permissions
{permissions_text}

# {self.Emojis.InsaneArhh}   Aliases
**{'**, **'.join(command.aliases) if command.aliases else f"-# {self.Emojis.UIA_Spinning}"}**
""",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else "https://c.tenor.com/KO80NCIjQAUAAAAd/tenor.gif")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362386665569779803/Silly_6.gif?ex=680234f4&is=6800e374&hm=c82b1ace8d364a1b641a17f1b7b08b548e566af3f38e3c8f537464d44e82db3d&")
        await self.smart_send(ctx, embed=embed, ephemeral=ephemeral)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                          >help CATEGORY                                          #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    async def send_cog_help(self, group: commands.Cog, ephemeral: bool = False):
        ctx = self.context
        embed = discord.Embed(
            description=f"""# {self.Emojis.random()} ・ Meo Help Center
Welcome to **Silly's** help menu! I'm here to assist you with all your **_silly_ needs.**

-# Use `{PREFIX}help [command]` or `/help [command]` for detailed help on a **specific command**.
-# Use `{PREFIX}help` or `/help` to see all **categories and commands**.
# {group.Emoji} __{group.qualified_name}__
""",
            color=discord.Color.green()
        )
        
        #logging.getLogger("silly").info(f"Sending group help for {group.qualified_name}")
        filtered = await self.filter_commands(group.get_commands(), sort=True)
        for idx, cmd in enumerate(filtered):
            CommandName = cmd.name
            CommandDescription = cmd.brief
            if cmd.hidden and not self.show_hidden:
                continue
            slash_cmd_id = INI.get('Slash_Commands', cmd.name, fallback=None)
            
            if slash_cmd_id:
                CommandName += f" (</{cmd.name}:{slash_cmd_id}>)"
            
            (RequiredParams, OptionalParams) = ([f"[{param.name}]" for param in cmd.clean_params.values() # Get clean params (filtered the self and ctx)
                                if param.default is param.empty # Check if param has a default value, if not, it's required
                                and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY) # Check if param is positional or keyword only
                                ],
                                                
                                [f"<{param.name}>" for param in cmd.clean_params.values() # Get clean params (filtered the self and ctx)
                                if param.default is not param.empty # Check if param has a default value, if yes, it's mot required
                                and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY) # Check if param is positional or keyword only
                                ] # Get optional params
            )
            
            
            embed.description += f"""{idx+1}. **{CommandName}{f" `{' '.join(RequiredParams)}`" if RequiredParams else ''}{f" `{' '.join(OptionalParams)}`" if OptionalParams else ''}**{f"\n-#  Aliases: **{'**, **'.join(cmd.aliases)}**" if cmd.aliases else ''}
> {repr(CommandDescription).strip('"').strip("'")}

"""
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else "https://c.tenor.com/KO80NCIjQAUAAAAd/tenor.gif")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362386665569779803/Silly_6.gif?ex=680234f4&is=6800e374&hm=c82b1ace8d364a1b641a17f1b7b08b548e566af3f38e3c8f537464d44e82db3d&")
        await self.smart_send(ctx, embed=embed, ephemeral=ephemeral)
        
        
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    #                                   ERROR WHEN COMMAND NOT FOUND                                   #
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
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
        await self.smart_send(ctx, embed=embed, delete_after=15)
        
    # ---------------------------------------------------------------------------- #
    #                       REPLACED COMMAND CALLBACK                              #
    # ---------------------------------------------------------------------------- #
    async def command_callback(self, ctx, *, command=None, ephemeral: bool = False):
        """The actual implementation of the help command."""
        logger.debug(f"Command callback called with ctx type: {type(ctx)}")
        
        # Set the context properly
        self.context = ctx
        
        # Set bot reference if needed
        if not hasattr(ctx, 'bot'):
            if isinstance(ctx, discord.Interaction):
                ctx.bot = ctx.client
            else:
                ctx.bot = self.context.bot

        if command is None:
            mapping = self.get_bot_mapping()
            return await self.send_bot_help(mapping, ephemeral=ephemeral)
        
        command_lower = command.lower()
        for cog in ctx.bot.cogs.values():
            if cog.qualified_name.lower() == command_lower:
                return await self.send_cog_help(cog, ephemeral=ephemeral)
        
        cmd = ctx.bot.get_command(command_lower)
        if cmd is not None:
            return await self.send_command_help(cmd, ephemeral=ephemeral)
        
        return await self.send_error_message(commands.CommandNotFound(f"**Uh oh, the command named `{command}` was not found!**"))
    
    def get_categories_and_commands_from_bot(self, bot: commands.Bot):
        categories_and_commands: Dict[str, List[commands.Command]] = {}

        for cog_name, cog in bot.cogs.items():
            if not cog.get_commands(): # empty cog
                continue
            categories_and_commands[f"[{cog_name.upper()}]"] = []
            for command in cog.get_commands():
                if command.hidden:
                    continue
                
                categories_and_commands[f"[{cog_name.upper()}]"].append(command)

        return categories_and_commands



class Utilities(commands.Cog, name="Meow Utilities"):
    Emoji = Emojis.UIA_Spinning
    def __init__(self, bot):
        self.bot = bot
        self.Emojis = Emojis
        self.help_command = Help()
        self.help_command.cog = self
        

    @BetterCommand(
        name="help",
        description="Let the silliest cat help you understand all commands!",
        brief="Let me tell you about **all commands**!",
        aliases=["pleasehelpmeimtoosilly"]
    )
    async def slash_help(self, ctx, *, option: str = None, ephemeral: bool = False):
        """I made this function to be able to use the help command in the slash command.

        Args:
            ctx (commands.Context): The context of the command.
            option (str, optional): The Command or Category you want to get help for. (Optional)
            ephemeral (bool, optional): Please send me secretly (only me can see it). (Default: False, Optional)
        """
        logger.debug(f"Slash help called with ctx type: {type(ctx)}")
        
        if isinstance(ctx, discord.Interaction):
            if not ctx.response.is_done():
                # Defer only if we haven't responded yet
                await ctx.response.defer(ephemeral=ephemeral)
                
        # Pass the context directly to the hidden _help command
        cmd = self.bot.get_command("_help")
        ctx.command = cmd  # Set the command context to _help
        await self.help_command.command_callback(ctx, command=option, ephemeral=ephemeral)
        
    @slash_help.autocomplete('option')
    async def command_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        self.categories_and_commands = self.help_command.get_categories_and_commands_from_bot(self.bot)
        
        choices = []
        for category, command in self.categories_and_commands.items():
            if current.lower() in category.lower():
                choices.append(app_commands.Choice(name=category, value=category.strip('[]').lower()))
            for cmd in command:
                if current.lower() in cmd.name.lower():
                    choices.append(app_commands.Choice(name=f"{PREFIX}{cmd.name}", value=cmd.name))
        
        
        return choices[:25]
    
    
    @BetterCommand(
        name="debug",
        description="Just show me the status of Silly. \nJust be cool and fun.",
        brief="**Silly** check-up",
        usage=f"""**Just easily** use `{PREFIX}debug` or `/debug` to check-up **Silly**""",
        aliases=["areyouok"]
    )
    async def debug(self, ctx: commands.Context, *, guild: bool = False, author: bool = False, ephemeral: bool = False):
        """Shows the bot's debug information
        
        Args:
            ctx (commands.Context): The context of the command.
            guild (bool, optional): Show guild information. (Default: False, Optional)
            author (bool, optional): Show author information. (Default: False, Optional)
            ephemeral (bool, optional): Please send me secretly (only me can see it). (Default: False, Optional)
        """
        
        
        embed = discord.Embed(
            description=f"""# {self.Emojis.random()} ・ Debug Information
## {self.Emojis.SecurityCat} Silly's Status Report

### {self.Emojis.CatEatingChips} Bot Information
> **ID**: `{self.bot.user.id}`
> **Version**: `{self.bot.__version__}`
> **discord.py**: `{discord.__version__}`
> **Python**: `{platform.python_version()}`
> **Github**: [Click here](https://github.com/pojo1807/Silly) plz star it ദ്ദി（• ˕ •マ.ᐟ
### {self.Emojis.CatScare} Technical Details
> **Memory Usage**: `{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB`
> **CPU Usage**: `{psutil.cpu_percent()}%`
> **Latency**: `{round(self.bot.latency * 1000)}ms`
> **Commands**: `{len(self.bot.commands)}`
> **Guilds**: `{len(self.bot.guilds)}`
> **Users**: `{len(self.bot.users)}`
""",
            color=discord.Color.blue()
        )
        
        # Guild Information
        if guild:
            guild_info = f"""> **Name**: {ctx.guild.name}
> **Owner**: {ctx.guild.owner.name} (`{ctx.guild.owner.id}`)
> **Created**: <t:{int(ctx.guild.created_at.timestamp())}:F>"""
            embed.add_field(
                name=f"{self.Emojis.UIA_Spinning} Guild Information (`{ctx.guild.id}`)", 
                value=guild_info,
                inline=False
            )
        
        if author:
            # get author avatar with alot sizes
            if ctx.author.avatar:
                avatar_1024 = ctx.author.avatar.url
                avatar_512 = ctx.author.avatar.url.replace("?size=1024", "?size=512")
                avatar_256 = ctx.author.avatar.url.replace("?size=1024", "?size=256")
                avatar_128 = ctx.author.avatar.url.replace("?size=1024", "?size=128")
                avatar_64 = ctx.author.avatar.url.replace("?size=1024", "?size=64")
                
                view_string = f"""[1024]({avatar_1024}) | [512]({avatar_512}) | [256]({avatar_256}) | [128]({avatar_128}) | [64]({avatar_64})"""
            else:
                view_string = f"{self.Emojis.UIA_Spinning} No avatar found"
            
            # Author Information  
            author_info = f"""> **Name**: {ctx.author.name}
    > **Avatar**: {view_string}
    > **Created**: <t:{int(ctx.author.created_at.timestamp())}:F>"""
            embed.add_field(
                name=f"{self.Emojis.Seriously} Author Information (`{ctx.author.id}`)",
                value=author_info,
                inline=False
            )
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else ctx.author.avatar.url if ctx.author.avatar else "https://c.tenor.com/KO80NCIjQAUAAAAd/tenor.gif")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1124562179635556362/1362386665569779803/Silly_6.gif?ex=680234f4&is=6800e374&hm=c82b1ace8d364a1b641a17f1b7b08b548e566af3f38e3c8f537464d44e82db3d&")
        await ctx.send(embed=embed, ephemeral=ephemeral)


    

async def setup(bot):
    await bot.add_cog(Utilities(bot))

    