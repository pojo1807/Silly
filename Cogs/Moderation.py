from typing import List
import discord
from discord.ext import commands
from discord.embeds import Embed
from discord.utils import MISSING
from discord import app_commands

from datetime import datetime

from Utils.Helper import Emojis
from Cogs.__init__ import BetterCommand, HelpFormat
from Utils.Globals import PREFIX

class Moderation(commands.Cog):
    
    Emoji = Emojis.SecurityCat
    def __init__(self, bot):
        self.Bot = bot
        self.Emojis = Emojis
        
    
        
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Ban ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ #
    @BetterCommand(
        name="ban",
        description="""Bans a member from the house and don't let he/she comeback.""",
        brief="**Bans** a member from **the house**.",
        help=
f"""Meowww! {Emojis.SecurityCat} Time to put on my serious face! (｀^´)

As the house's security kitty, I take my job of keeping our cozy home safe very seriously! *adjusts tiny security badge*

When someone's being a real troublemaker and you need my help:
- I'll give them the ultimate time-out - a **ban** from our server! {Emojis.CatScare}
- They won't be able to sneak back in either (unless you decide to forgive them later~)

Just remember my little rules, okay? {Emojis.JustWokeUp}
- You need special `Ban Members` powers to ask for my help
- I can't ban anyone stronger than you (even cats have limits!)
- Let's use this carefully! We want to protect our home, not make it scary {Emojis.NerdCat}

*purrrr... Just tell me who's been naughty and I'll take care of the rest! ฅ^•ﻌ•^ฅ*""",
        usage=f"""
This is how you can use it to **ban**:
{HelpFormat(f"{PREFIX}ban", ["member"], ["reason", "delete_messages_days"])}""",
    )
    @commands.has_permissions(ban_members=True)
    @app_commands.choices(
        delete_messages_days=[
            app_commands.Choice(name="Don't delete any messages", value=0),
            app_commands.Choice(name="Delete messages from last 24 hours", value=1), 
            app_commands.Choice(name="Delete messages from last 2 days", value=2),
            app_commands.Choice(name="Delete messages from last 3 days", value=3),
            app_commands.Choice(name="Delete messages from last 5 days", value=5),
            app_commands.Choice(name="Delete messages from last week", value=7)
        ]
    )
    
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None, delete_messages_days: int = 0):
        """Bans a member from the server.
        This command requires the `ban_members` permission.

        Args:
            ctx (commands.Context): Context of the command.
            member (discord.Member): The hooman you want to BAN. (muhehehehehehe)
            reason (str, optional): Why you want to ban this silly one?
            delete_messages_days (int, optional): How many days of messages to delete. (Default: Don't delete any messages)
        """
        
        embed = Embed(
            timestamp=datetime.now(),
        )
        
        # ---------------------------------- Ban Bot --------------------------------- #
        if ctx.guild.me == member:
            embed.description = f"""# {self.Emojis.SecurityCat} ・ Trust Issue
## {self.Emojis.CatScare} *_glup_...
# Why do you want to ban me?
# Am I not a good cat? 
# Am I not enough good for you?
# Am I not enough silly for you?


Please check again **who you want to ban**

-# I'm surely you didn't mean me... {self.Emojis.JustWokeUp} """
            embed.color = discord.Color.yellow()
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1202085160888307742/1202085161060007956/cat-cats.gif?ex=6804628c&is=6803110c&hm=cbb6c517adc24078f85c5e5ec93ab8e714fe22994e0c69e7a820eda766ec0f89&")
            embed.set_image(url="https://media.discordapp.net/attachments/982449621290868826/1000041688326230096/09-55-29-IMG_0787.gif?ex=68045726&is=680305a6&hm=de229dff9f40711b991cc741e93c5cc99fb87506632592be93250dbb1dff7d38&")
            await ctx.send(embed=embed)
            
            return
        
        # ------------------------------- Ban Yourself ------------------------------- #
        if ctx.author == member:
            embed.description = f"""# {self.Emojis.SecurityCat} ・ Silly Detected
**Why you _sillier_ than me...**
You *cannot* ban **yourself**.

Please check again **who you want to ban**,
-# maybe *misspelled*?? {self.Emojis.CatLaughAndPointing * 3} """
            embed.color = discord.Color.red()
            embed.set_image(url="https://c.tenor.com/nen_hthCrhAAAAAd/tenor.gif")
            embed.set_thumbnail(url="https://c.tenor.com/Oas_7V6NajEAAAAd/tenor.gif")
            await ctx.send(embed=embed)
            return
        
        if ctx.author.top_role.position <= member.top_role.position:
            embed.description = f"""# {self.Emojis.SecurityCat} ・ Permissions Issue
## {self.Emojis.CatScare} *_glup_...
The member you want to ban is **higher** or **same** as you.

**{ctx.author.mention} (you)**: `{ctx.author.top_role.position}th ({ctx.author.top_role.name})`
**{member.mention} (member)**: `{member.top_role.position}th ({member.top_role.name})`

## Please check again **who you want to ban**, maybe *misspelled*?? {self.Emojis.JustWokeUp} """
            embed.color = discord.Color.yellow()
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/422448194476048403/1312836732554576003/togif-1_1.gif?ex=6800953c&is=67ff43bc&hm=57f6fa3cceda68201a082c04ab4dcc7e8b719f91f427771fdeecd8c4a36c5729&")
            embed.set_image(url="https://c.tenor.com/bUpZ5QOU5xIAAAAd/tenor.gif")
            await ctx.send(embed=embed)
            
            return
        
        
        reason = reason or "No meosen."
        
        
        
        # ----------------------------- Check if bot can ban ----------------------------- #
        if ctx.guild.me.top_role.position <= member.top_role.position:
            embed.description = f"""# {self.Emojis.SecurityCat} ・ Permissions Issue
## **HEY**, I am Security Cat, I am **not allowed** to ban this hooman because *he/she* is **higher** or **same** as me!
Hmm, to fix this problem, follow these steps (veri easy!!!):
1. Go to **Server Settings** {self.Emojis.BTNSettings}
2. In **People** category, click on **Roles**
3. Find '{self.Emojis.ICONRole} Silly'
4. When you found it, hover on it and you can see the drag icon {self.Emojis.ICONDrag}, **click and hold** it to the top of the list or at least highest.
5. Now, you can use me to ban **this hooman**! {self.Emojis.CatEatingChips}"""
            embed.color = discord.Color.yellow()
            embed.set_image(url="https://media.discordapp.net/attachments/1202085160888307742/1202085161060007956/cat-cats.gif?ex=6804628c&is=6803110c&hm=cbb6c517adc24078f85c5e5ec93ab8e714fe22994e0c69e7a820eda766ec0f89&")
            await ctx.send(embed=embed)
            return
        
        # ----------------------------- Ban Member ----------------------------- #
        
        embed.description = f"""# {self.Emojis.SecurityCat} ・ Banned!
## {self.Emojis.SecurityCat} I have **MEOW** this hooman from the house.
-# You know, he/she is a **bad hooman** and he/she is **not allowed** to be in the house.

## "I'm sorry, I gave you wrong information or I want to unban this hooman."
Easy! You can use me to **unban** this hooman.
- Just type `{PREFIX}unban <@member>` or `/unban <@member>`. I will **unban this hooman** for you.
"""
        embed.add_field(name=f"{self.Emojis.Seriously} Member", value=f"{member.mention} ({member.id})", inline=True)
        embed.add_field(name=f"{self.Emojis.CatScare} Reason", value=reason, inline=True)
        embed.add_field(name="_ _", value="_ _", inline=False) # new line
        embed.add_field(name=f"{self.Emojis.CatEatingChips} Banned by", value=ctx.author.mention, inline=True)
        embed.add_field(name=f"{self.Emojis.UIA_Spinning} Banned at", value=f"<t:{int(embed.timestamp.timestamp())}:F>", inline=True)
        embed.color = discord.Color.green()
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1312448853450162176/1312448878414397603/IMG_7880.gif?ex=68047204&is=68032084&hm=b46ba243a8cf030d8c222c0370ed9aa8e097f4544cbc64b102ccd8a281a13602&")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1218440992651218959/1255879183931019294/image_2024-06-27_213452161.gif?ex=6804f822&is=6803a6a2&hm=3d6faf4c46d121831e594e0430c61ac45318df514998ef42a5b673644b475384&")
        await ctx.send(embed=embed)
        await member.ban(reason=reason, delete_message_days=delete_messages_days)



async def setup(bot):
    await bot.add_cog(Moderation(bot))
