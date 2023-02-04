import discord
import traceback
from discord.ext import commands
from os import getenv
import random
import typing
import emoji
import sqlite3
from discord import TextChannel, VoiceChannel, Role, Intents

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print(f"{client.user}でログインしました")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send("指定したチャンネルが見つかりません")
    elif isinstance(error, commands.CommandNotFound):
        return
    raise error


@client.command()
async def shuffle(ctx,
                  host1: typing.Optional[Role] = None,
                  host2: typing.Optional[Role] = None,
                  host3: typing.Optional[Role] = None,
                  host4: typing.Optional[Role] = None,
                  *channels: VoiceChannel):
    if not ctx.guild.get_role(968160313797136414) in ctx.author.roles:
        await ctx.send("実行権限がありません")
        # return
    if ctx.author.voice is None:
        await ctx.send("ボイスチャンネルに入ってください")
        return
    if len(channels) == 0:
        await ctx.send("ボイスチャンネルを指定してください")
        return
    channel = ctx.author.voice.channel

    members = channel.members
    hosts = []

    for m in members[:]:
        if host1 is not None and host1 in m.roles:
            hosts.append(m)
            members.remove(m)
            continue

        if host2 is not None and host2 in m.roles:
            hosts.append(m)
            members.remove(m)
            continue

        if host3 is not None and host3 in m.roles:
            hosts.append(m)
            members.remove(m)
            continue

        if host4 is not None and host4 in m.roles:
            hosts.append(m)
            members.remove(m)
            continue

    random.shuffle(members)
    random.shuffle(hosts)

    for i in range(len(members)):
        await members[i].move_to(channels[i % len(channels)])
    for i in range(len(hosts)):
        await hosts[i].move_to(channels[i % len(channels)])

    await ctx.send(f"{channel.mention}に接続している人を移動させました")


token = getenv('DISCORD_BOT_TOKEN')
client.run(token)
