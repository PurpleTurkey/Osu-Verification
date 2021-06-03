import asyncio
import json
import os
import sys
import time
import copy
import datetime
import shutil

import discord
import discord.ext.commands as commands
from discord.utils import get
from discord import Intents

from auxiliary.constants import *
from banchoirc import *

import threading
from tinydb import TinyDB, Query

from cogs.verify import VerifyCog 
from cogs.help import HelpCog
from cogs.admin import AdminCog


# Load config
with open(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'config.json')) as f:
    config_data = json.load(f)

# Load database
db = TinyDB(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'database.json'))
db_users = db.table('users', cache_size=0)
db_guilds = db.table('guilds', cache_size=0)

intents = discord.Intents(members=True, guilds=True)

PREFIX = config_data['PREFIX']
DISCORD_TOKEN = config_data['DISCORD_TOKEN']
client = commands.Bot(command_prefix=PREFIX, description=config_data['STATUS'],chunk_guilds_at_startup=False)
client.remove_command("help")



# COGS
client.add_cog(VerifyCog(client, db, config_data))
client.add_cog(HelpCog(client, config_data))
client.add_cog(AdminCog(client, db, config_data))


async def review_database():

    while True:
        minutes = 0.5
        await asyncio.sleep(int(60*minutes))

        table = db_users
        Users = Query()
        results = table.search(Users.verification_error != "")

        for user in results:
            status = user['verification_error']

            if status == "success":
                desc = [
                    "```",
                    "Your account has been successfully linked to",
                    f"osu! user: {user['osu_user']}",
                    "```"
                ]
                embed = discord.Embed(title="Verification Success", description="\n".join(
                    desc), color=GREEN)
            elif status == "already_verified":
                desc = [
                    "```",
                    "Your discord account is already linked to",
                    f"osu! user: {user['osu_user']}",
                    "```"
                ]
                embed = discord.Embed(title="Verification Error", description="\n".join(
                    desc), color=ORANGE)
            elif status == "code_timeout":
                desc = [
                    "```",
                    "Your verification code has timed out!",
                    f"Please use {config_data['PREFIX']}verify to generate a new code",
                    "```"
                ]
                embed = discord.Embed(title="Verification Error", description="\n".join(
                    desc), color=RED)
            elif status == "user_already_linked":
                desc = [
                    "```",
                    "This osu! user is already linked to a discord account!",
                    "```"
                ]
                embed = discord.Embed(title="Verification Error", description="\n".join(
                    desc), color=RED)

            
            disc_user = await client.fetch_user(int(user['discord_user']))
            await disc_user.send("", embed=embed)

            # Update user so that verification_error is reset
            user['verification_error'] = ""
            table.upsert(user, Users.discord_user == str(disc_user.id))

            if status == "success":
                desc = [
                    "```",
                    "Now that you are verified, in servers that support OsuVerification, use the command",
                    f"{config_data['PREFIX']}verify server",
                    "to gain a 'verified' role and nickname",
                    "```",
                    "Note: This only works if the discord server has this feature enabled"
                ]
                embed = discord.Embed(title="Server Verification", description="\n".join(
                    desc), color=LIGHT_BLUE)
                await disc_user.send("", embed=embed)
async def update_status():
    while True:

        table = db_users
        Users = Query()
        results = table.search(Users.verified == True)

        total_verified_users = len(results)
        activity = discord.Game(name=f"{config_data['PREFIX']}help | {total_verified_users} verified osu! players")
        await client.change_presence(status=discord.Status.online, activity=activity)

        minutes = 0.2
        await asyncio.sleep(int(60*minutes))

async def daily_backup():

    while True:
        
        date = datetime.datetime.now()
        
        new_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0]))) + "/db_backups/"
        new_file_name = f"{date.month}_{date.day}_{date.year}_save" + ".json"

        if not os.path.exists(new_path+new_file_name):
            shutil.copyfile("database.json",new_path+new_file_name)

        minutes = 60*24
        await asyncio.sleep(int(60*minutes))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    print("------------")

    activity = discord.Game(name=f"{config_data['STATUS']}")
    await client.change_presence(status=discord.Status.online, activity=activity)

    client.loop.create_task(review_database())
    client.loop.create_task(update_status())
    client.loop.create_task(daily_backup())

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            pass

    table = db_guilds
    Guilds = Query()
    results = table.search(Guilds.id == str(guild.id))

    if results != []: # already joined before
        pass
    else:

        guild_ = {
            'id' : str(guild.id),
            'role' : None,
            'nicknames' : True
        }
        table.insert(guild_)

@client.command(pass_context=True)
async def embedmessage(ctx, val : str = None):
    return
    desc = [
            "item1",
            "item2"
    ]
    embed = discord.Embed(title="Rank to PP", description="\n".join(
        desc), color=0x56fc77)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
        icon_url=ctx.author.avatar_url)
    await ctx.send("", embed=embed)
    # end method
    return

@client.command(pass_context=True)
async def user(ctx, user: discord.User=None):

    if user == None:
        desc = [
            "```",
            "Please specifiy a user!",
            f"{config_data['PREFIX']}user @discorduser",
            "```"
        ]
        embed = discord.Embed(title="Invalid User", description="\n".join(
            desc), color=RED)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
            icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)
    
    table = db_users
    Users = Query()
    results = table.search(Users.discord_user == str(user.id))

    if results != []:
        curr_user = results[0]
        if curr_user['verified'] == True:

            signature = f"http://lemmmy.pw/osusig/sig.php?colour=hexff66aa&uname={curr_user['osu_user']}&countryrank&flagstroke&darktriangles&onlineindicator=undefined&xpbar"
            desc = [
                "```",
                "Status: Verified ✅",
                "```"
            ]
            embed = discord.Embed(title=f"{user.name}/{curr_user['osu_user']}", description="\n".join(
                        desc), color=PINK)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            embed.set_image(url=signature)

            await ctx.send("", embed=embed)
            return
    
   
    desc = [
        "```",
        "Status: Not Verified ❌",
        "```"
    ]
    embed = discord.Embed(title=f"{user.name}/Unknown", description="\n".join(
                desc), color=PINK)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
                icon_url=ctx.author.avatar_url)

    await ctx.send("", embed=embed)

@client.command(pass_context=True)
async def ping(ctx):
    await ctx.send(f'Pong! `{round(client.latency,3)}s` reply')

@client.command(pass_context=True)
async def patchnotes(ctx):
    desc = [
        "Version - **0.7**",
        "Last Updated - **6/2/2021**",
        "\> Long-term database support",
        "\> Verification system added",
        "Bot created by Turkey#3157"
    ]
    embed = discord.Embed(title="Patch Notes", description="\n".join(
        desc), color=PURPLE)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
        icon_url=ctx.author.avatar_url)
    await ctx.send("", embed=embed)

@client.command(pass_context=True)
async def invite(ctx):

    embed = discord.Embed(title="Invite Link", description="[Click Here](https://discord.com/api/oauth2/authorize?client_id=849718485910814761&permissions=470641728&scope=bot)", color=PURPLE)
    embed.set_footer(text="Requested by " + str(ctx.author.name),
        icon_url=ctx.author.avatar_url)
    await ctx.send("", embed=embed)


@client.event
async def on_message(message):

    if message.author.id is client.user.id:
        return    

    await client.process_commands(message)

client.run(DISCORD_TOKEN, bot=True)
