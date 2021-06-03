import asyncio
import time
import discord
from discord.ext import commands
from auxiliary.constants import *
from tinydb import TinyDB, Query

class AdminCog(commands.Cog):
    def __init__(self, client, db, config):
        
        self.client = client
        self.db = db
        self.guild_table = self.db.table('guilds', cache_size=0)
        self.config_data = config

    @commands.group(pass_context=True)
    async def admin(self, ctx):
        prefix = self.config_data['PREFIX']
        if ctx.invoked_subcommand in [None]:
            desc = [
                "```",
                "Did you mean:",
                f"{prefix}admin menu"
                "```"
            ]

            embed = discord.Embed(title="Request Error", description="\n".join(
            desc), color=ORANGE)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)

    @admin.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def nicknames(self, ctx, toggle):

        if toggle in ("true", "false"):
            table = self.guild_table
            Guilds = Query()
            results = table.search(Guilds.id == str(ctx.message.guild.id))
            guild_ = results[0]
        else:
            desc = [
                "```",
                "Improper usage, try:",
                "o-admin nicknames true",
                "or",
                "o-admin nicknames false"
                "```"
            ]

            embed = discord.Embed(title="Request Error", description="\n".join(
            desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)
            return

        if toggle == "true":
            guild_['nicknames'] = True
            enabled_status = "ENABLED"
        elif toggle == "false":
            guild_['nicknames'] = False
            enabled_status = "DISABLED"
        
        table.upsert(guild_, Guilds.id == str(ctx.message.guild.id))

        desc = [
            "```",
            f"Server nicknames now {enabled_status}"
            "```"
        ]

        embed = discord.Embed(title="Admin Menu", description="\n".join(
        desc), color=GREEN)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)

    @admin.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def role(self, ctx, role: discord.Role):

        try:
            z = role.color
        except:

            desc = [
                "```",
                "Invalid role!"
                "Did you mean:",
                f"{prefix}admin role @role",
                "```",
                "Note: tag the role you want to set"
            ]

            embed = discord.Embed(title="Request Error", description="\n".join(
            desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)

        
        table = self.guild_table
        Guilds = Query()
        results = table.search(Guilds.id == str(ctx.message.guild.id))
        guild_ = results[0]

        guild_['role'] = str(role.id)
        table.upsert(guild_, Guilds.id == str(ctx.message.guild.id))

        desc = [
            "```",
            f"Server's designated verification role is now @{str(role.name)}"
            "```"
        ]

        embed = discord.Embed(title="Admin Menu", description="\n".join(
        desc), color=GREEN)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)


    @admin.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def menu(self, ctx):
        prefix = self.config_data['PREFIX']

        desc = [
            "**Set verified role**",
            f"`{prefix}admin role @role`",
            f"gives a user the specific role, when using {prefix}verify server\n",
            f"**osu! Nicknames**",
            f"`{prefix}admin nicknames true/false` use true OR false",
            f"nicknames a user their osu! username, when using {prefix}verify server"
        ]

        embed = discord.Embed(title="Admin Menu", description="\n".join(
        desc), color=BLUE)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)