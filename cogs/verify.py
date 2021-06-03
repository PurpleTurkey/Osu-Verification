import asyncio
import time
import discord
from discord.utils import get
from discord.ext import commands
import auxiliary.constants as constants
from auxiliary.constants import *
from auxiliary.generatecode import *
from tinydb import Query

class VerifyCog(commands.Cog):
    def __init__(self, client, db, config):
        
        self.client = client
        self.db = db
        self.user_table = self.db.table('users', cache_size=0)
        self.guild_table = self.db.table('guilds', cache_size=0)
        self.config_data = config

    @commands.group(pass_context=True)
    async def verify(self, ctx):
        
        if ctx.invoked_subcommand in [None]:

            # Check if user is already in database
            table = self.user_table # unlimited cache size may increase speed, but also can be wonky
            Users = Query()
            results = table.search(Users.discord_user == str(ctx.author.id))

            if results != []: # TODO: or account for if code has not been verified

                user = results[0]

                if user['verified'] == True:
                    desc = [
                    "```",
                    "Your discord account is already linked to an osu! account.",
                    "```"
                    ]
                    embed = discord.Embed(title="Account already verified!", description="\n".join(
                    desc), color=ORANGE)
                    embed.set_footer(text="Requested by " + str(ctx.author.name),
                                icon_url=ctx.author.avatar_url)
                    await ctx.send("", embed=embed)
                    return

            # else
            desc = [
                "```"
                "A verification code has been sent to you!",
                "Check the direct message for further instruction.",
                "```"
            ]
            embed = discord.Embed(title="Verification code sent!", description="\n".join(
            desc), color=GREEN)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)


            # Generate code and update database
            code = gen_code()
            user = {
                "discord_user" : str(ctx.author.id),
                "verified" : False,
                "osu_user" : None,
                "last_code" : code,
                "last_code_time_sent" : time.time(),
                "verification_error" : "",
                "verified_osu_list" : []
            }
            table.upsert(user, Users.discord_user == str(ctx.author.id))


            # Send dm to user
            desc = [
                "**Code**",
                f"`{code}`",
                "```",
                "1. Copy the code above",
                "2. Open osu! and start a chat with user: PurpleTurkey",
                "3. Paste the code and send it to PurpleTurkey",
                "Please ensure that there are no additional characters or spaces when sending the code"
                "```"
            ]
            embed = discord.Embed(title="Verification Instructions", description="\n".join(
            desc), color=BLUE)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            await ctx.author.send("", embed=embed)

    @verify.command(pass_context=True)
    async def reset(self, ctx):

            table = self.user_table # unlimited cache size may increase speed, but also can be wonky
            Users = Query()
            results = table.search(Users.discord_user == str(ctx.author.id))

            if results != []:
                curr_user = results[0]
                if curr_user['osu_user'] != None:

                    desc = [
                        "```"
                        f"By resetting your account, this discord account will not longer be associated with osu! user {curr_user['osu_user']}",
                        "To proceed, react with : ✔️",
                        "To cancel, react with  : ❌",
                        "```",
                        "This will timeout in 2 minutes"
                    ]

                    embed = discord.Embed(title="Reset Account", description="\n".join(
                    desc), color=ORANGE)
                    embed.set_footer(text="Requested by " + str(ctx.author.name),
                                icon_url=ctx.author.avatar_url)
                    msg = await ctx.send("", embed=embed)

                    start_time = time.time()
                    timeout = 60*2 # in seconds
                    await msg.add_reaction("\U00002705") # Check
                    await msg.add_reaction("\U0000274c") # X

                    while time.time() - start_time <= timeout:
                        def check(reaction, user):
                            return user == ctx.author and str(reaction.emoji) in ["\U00002705","\U0000274c"]

                        try:
                            reaction, user = await self.client.wait_for('reaction_add', timeout=(5), check=check)
                        except asyncio.TimeoutError:
                            pass
                        else:
                            if str(reaction.emoji) == "\U00002705": # check
                                embed.color = GREEN
                                desc2 = [
                                    "**Status**",
                                    "```Account successfully RESET```"
                                ]
                                embed.description = "\n".join(desc[:-1]) + "\n".join(desc2)
                                await msg.edit(embed=embed)

                                curr_user['verified'] = False
                                curr_user['osu_user'] = None

                                table.upsert(curr_user, Users.discord_user == str(ctx.author.id))

                                return
                            elif str(reaction.emoji) == "\U0000274c": # X
                                embed.color = GREEN
                                desc2 = [
                                    "**Status**",
                                    "```Action CANCELLED```"
                                ]
                                embed.description = "\n".join(desc[:-1]) + "\n".join(desc2)
                                await msg.edit(embed=embed)
                                return
                        

                            await msg.edit(embed=pages[current_page])

                    return
            
            # no account linked 

            desc = [
                "```"
                "You are not currently verified with an osu! account",
                "Please use the command:",
                "```",
                "```"
                f"{self.config_data['PREFIX']}verify",
                "```"
            ]

            embed = discord.Embed(title="Request Error", description="\n".join(
            desc), color=RED)
            embed.set_footer(text="Requested by " + str(ctx.author.name),
                        icon_url=ctx.author.avatar_url)
            await ctx.send("", embed=embed)

    @verify.command(pass_context=True)
    async def server(self, ctx):

        # nicknames
        table = self.user_table # unlimited cache size may increase speed, but also can be wonky
        Users = Query()
        results = table.search(Users.discord_user == str(ctx.author.id))

        if results != []:
            curr_user = results[0]
            if curr_user['verified'] == True:

                pass
            else:
                return
        else:
            return

        # Now 100% verified

        table = self.guild_table
        Guilds = Query()
        results = table.search(Guilds.id == str(ctx.message.guild.id))
        guild_ = results[0]

        if guild_['nicknames'] == True:
            
            try:
                await ctx.author.edit(nick=curr_user['osu_user'])
                await ctx.author.send(f"```Your nickname has been changed on {ctx.message.guild.name}```")
            except:
                await ctx.author.send(f"```Attempted to change your nickname (bots cannot change server admins' nicknames [unless also an admin])```")
        if guild_['role'] != None:
            role_id = int(guild_['role'])
            role = get(ctx.message.guild.roles, id=role_id)
            try:
                await ctx.author.add_roles(role)
                await ctx.author.send(f"```You have been given a 'Verified' role on {ctx.message.guild.name}```")
            except:
                 await ctx.author.send(f"```Attempted to give you a role on {ctx.message.guild.name}, but the server has improperly configured this option.```")



    @verify.command(pass_context=True)
    async def help(self, ctx):
        prefix = self.config_data['PREFIX']
        desc = [
                f"```{prefix}verify help```",
                f"`{prefix}verify`   verify your osu! & discord accounts",
                f"`{prefix}verify server`   if verified, register with the server that this command is used in",
                f"`{prefix}verify reset`    reset your verified account`"
            ]

        embed = discord.Embed(title="Verification Commands", description="\n".join(
        desc), color=PINK)
        embed.set_footer(text="Requested by " + str(ctx.author.name),
                    icon_url=ctx.author.avatar_url)
        await ctx.send("", embed=embed)
    