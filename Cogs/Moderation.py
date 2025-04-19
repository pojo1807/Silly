import discord
from discord.ext import commands
from discord.embeds import Embed

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
        description="Bans a member from the house. that means this person won't give me food and pet me anymore... 😿",
        brief="Bans a member from the house",
        help=
f"""# {Emojis.SecurityCat} ・ Ban Command
**Bans a member from the house and don't let _he/she_ comeback.**
""",
        usage=f"""
This is how you can use it to **ban**:
{HelpFormat(f"{PREFIX}ban", ["member"], ["reason"])}""",
    )
    @commands.has_permissions(ban_members=True)
    
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = None):
        """Bans a member from the server.
        This command requires the `ban_members` permission.

        Args:
            ctx (commands.Context): Context of the command.
            member (discord.Member): The hooman you want to BAN. (muhehehehehehe)
            reason (str, optional): Why you want to ban this silly one?
        """
        reason = reason or "No meosen."
        embed = Embed(
            timestamp=datetime.now(),
        )
        
        if ctx.author == member:
            embed.description = f"""# {self.Emojis.SecurityCat} ・ Silly Detected
**Why you _sillier_ than me...**
You *cannot* ban **yourself**.
Please check again **who you want to ban**,
-# maybe *misspelled*?? {self.Emojis.CatLaughAndPointing} """
            embed.color = discord.Color.red()
            embed.set_image(url="https://c.tenor.com/nen_hthCrhAAAAAd/tenor.gif")
            embed.set_thumbnail(url="https://c.tenor.com/Oas_7V6NajEAAAAd/tenor.gif")
            await ctx.send(embed=embed)
            return
        
        if ctx.author.top_role <= member.top_role:
            embed.description = f"""# {self.Emojis.SecurityCat} ・ Permissions Issue
{self.Emojis.CatScare} *_glup_...
Who you wanted to ban is higher than you.
Please check again **who you want to ban**, maybe *misspelled*?? {self.Emojis.JustWokeUp} """
            embed.color = discord.Color.yellow()
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/422448194476048403/1312836732554576003/togif-1_1.gif?ex=6800953c&is=67ff43bc&hm=57f6fa3cceda68201a082c04ab4dcc7e8b719f91f427771fdeecd8c4a36c5729&")
            embed.set_image(url="https://c.tenor.com/bUpZ5QOU5xIAAAAd/tenor.gif")
            await ctx.send(embed=embed)
            
            return
        
        if ctx.guild.me.top_role <= member.top_role:
            embed.description = f"""# {self.Emojis.SecurityCat} ・ Permissions Issue
{self.Emojis.SecurityCat} **HEY**, I am Security Cat, I am **not allowed** to ban this hooman because *he/she* is __higher__ than me!
Hmm, to fix this problem, follow these steps (veri easy!!!):
1. Go to **Server Settings** {self.Emojis.BTNSettings}
2. In **People** category, click on **Roles**
3. Find '{self.Emojis.ICONRole} Silly'
4. When you found it, hover on it and you can see the drag icon {self.Emojis.ICONDrag}, **click and hold** it to the top of the list or at least highest.
5. Now, you can use me to ban **this hooman**! {self.Emojis.CatEatingChips}"""
            embed.color = discord.Color.yellow()
            embed.set_image(url="https://media1.tenor.com/m/DFfCL02_DCcAAAAd/cat-look.gif")
            await ctx.send(embed=embed)
            return
        

        await member.ban(reason=reason)
        embed.description = f"""# {self.Emojis.SecurityCat} ・ Banned!
{self.Emojis.SecurityCat} I have **meow** this hooman from the house.
"""
        embed.add_field(name=f"{self.Emojis.Seriously} Member", value=f"{member.mention} ({member})", inline=True)
        embed.add_field(name=f"{self.Emojis.CatScare} Reason", value=reason, inline=True)
        embed.add_field(name="_ _", value="_ _", inline=False) # new line
        embed.add_field(name=f"{self.Emojis.CatEatingChips} Banned by", value=ctx.author.mention, inline=True)
        embed.add_field(name=f"{self.Emojis.UIA_Spinning} Banned at", value=f"<t:{int(embed.timestamp.timestamp())}:F>", inline=True)
        embed.color = discord.Color.green()
        
        embed.set_image(url="https://media.discordapp.net/attachments/1094235464933851136/1099656380572520509/ezgif-2-a32162a0c1.gif?ex=67ff92cf&is=67fe414f&hm=b185533edd7334a3cb7aa1f2e0a57fbbe273edceff2a2fc4834f78c688268330&size=1024&")
        await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Moderation(bot))
