import asyncio
import time
import discord
from discord.ext import commands
from auxiliary.constants import *

class HelpCog(commands.Cog):
    def __init__(self, client, config):
        
        self.client = client
        self.config_data = config

    @commands.group(pass_context=True)
    async def help(self, ctx):
        prefix = self.config_data['PREFIX']
        if ctx.invoked_subcommand in [None]:

            desc = [
                f"```{prefix}verify```",
                "```",
                f"{prefix}verify help",
                f"{prefix}admin menu (requires admin permissions)"
                "```",
                "```",
                f"{prefix}user @discorduser",
                "```"
            ]

            embed = discord.Embed(title="Help Menu", description="\n".join(
            desc), color=PINK)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            embed.add_field(name="Other Commands",value=f"`{prefix}patchnotes`, `{prefix}invite`, `{prefix}ping`", inline=False)
            await ctx.send("", embed=embed)