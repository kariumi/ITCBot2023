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

"""
!shuffle
自分が入っているボイスチャンネルの人を指定したボイスチャンネルにランダムに振り分け、自動的に移動させるコマンドです。

!shuffle [ボイスチャンネルID 1] [ボイスチャンネルID 2] ...
例：!shuffle 123456789012345678 123456789012345679
上記のように指定すると、指定したボイスチャンネルにランダムに振り分けることができます。

!shuffle [(任意)ロール 1] [(任意)ロール 2] [(任意)ロール 3] [ボイスチャンネルID 1] [ボイスチャンネルID 2] ...
例：!shuffle @DTM部 @CG部 123456789012345678 123456789012345679
上記のようにロールを指定すると、指定したロールのメンバーは均等に振り分けられます。
・ロールは0~3個の間で指定することができます。
(created by Chino)
"""


@client.command()
async def shuffle(ctx, host1: typing.Optional[Role] = None, host2: typing.Optional[Role] = None, host3: typing.Optional[Role] = None, *channels: VoiceChannel):
    if not ctx.guild.get_role(968160313797136414) in ctx.author.roles:
        await ctx.send("実行権限がありません")
        return
    if ctx.author.voice is None:
        await ctx.send("ボイスチャンネルに入ってください")
        return
    if len(channels) == 0:
        await ctx.send("ボイスチャンネルを指定してください")
        return
    channel = ctx.author.voice.channel  # 実行者の入っているチャンネル

    members = channel.members  # channelに入っている全メンバーをmenbersに追加
    hosts1, hosts2, hosts3 = []

    for m in members[:]:
        if host1 is not None and host1 in m.roles:
            hosts1.append(m)
            members.remove(m)
            continue

        if host2 is not None and host2 in m.roles:
            hosts2.append(m)
            members.remove(m)
            continue

        if host3 is not None and host3 in m.roles:
            hosts3.append(m)
            members.remove(m)
            continue

    random.shuffle(members)
    random.shuffle(hosts1)
    random.shuffle(hosts2)
    random.shuffle(hosts3)

    for i in range(len(members)):
        await members[i].move_to(channels[i % len(channels)])
    for i in range(len(hosts1)):
        await hosts1[i].move_to(channels[i % len(channels)])
    for i in range(len(hosts2)):
        await hosts2[i].move_to(channels[i % len(channels)])
    for i in range(len(hosts3)):
        await hosts3[i].move_to(channels[i % len(channels)])

    await ctx.send(f"{channel.mention}に接続している人を移動させました")

"""
!vote
投票を作成するコマンド

!vote create [投票タイトル] [投票先1] [投票先2] [投票先3] ...
投票を作成してくれます。

!vote list_up [メッセージID]
投票したメンバーを表示します。

"""


@client.command()
async def vote(ctx, *args):
    if not ctx.guild.get_role(968160313797136414) in ctx.author.roles:
        await ctx.send("実行権限がありません")
        return

    if args[0] == "create":
        vote_title = args[1]
        vote_list = []
        vote_icon = [":one:", ":two:", ":three:", ":four:",
                     ":five:", ":six:", ":seven:", ":eight:", ":nine:"]
        for i in range(len(args[1:])):
            mes += f"{vote_icon[i]} {args[i+1]}\n"
        message = await ctx.send(f"【投票】"
                                 f"{vote_title}\n"
                                 f"\n"
                                 f"{mes}")
        for i in range(len(args[1:])):
            await message.add_reaction(vote_icon[i])

    elif args[0] == "list_up":
        pass
    else:
        await ctx.send("Error:引数が認識されませんでした。\n"
                       "```\n"
                       "!vote create [投票タイトル] [投票先1] ...\t投票を作成します。\n"
                       "!vote list_up [メッセージID]\t投票結果を表示します。"
                       "```")


token = getenv('DISCORD_BOT_TOKEN')
client.run(token)
