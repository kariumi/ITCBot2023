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
intents.reactions = True
intents.members = True


client = commands.Bot(command_prefix='!', intents=intents)

authority_role = ["", ""]


@client.event
async def on_ready():
    print(f"{client.user}でログインしました")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send(embed=any_error("指定したチャンネルが見つかりません"))
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
    if not ctx.guild.get_role(968160313797136414) in ctx.author.roles and not ctx.guild.get_role(1071476455348903977) in ctx.author.roles:
        await ctx.send(embed=authority_error())
        return
    if ctx.author.voice is None:
        await ctx.send(embed=any_error("ボイスチャンネルに入ってください", ""))
        return
    if len(channels) == 0:
        await ctx.send(embed=any_error("ボイスチャンネルを指定してください", ""))
        return
    channel = ctx.author.voice.channel  # 実行者の入っているチャンネル

    members = channel.members  # channelに入っている全メンバーをmenbersに追加
    hosts1 = []
    hosts2 = []
    hosts3 = []

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
投票を作成して色々できる

!vote create [テキストチャンネルID] [投票タイトル] [投票先1] [投票先2] [投票先3] ...
投票を作成してくれます。

!vote role [テキストチャンネルID] [テキストメッセージID] [投票番号] [ロール]
ロールを付与できます。

"""


@client.command()
async def vote(ctx, arg=None, channel: typing.Optional[TextChannel] = None, *args):
    if not ctx.guild.get_role(968160313797136414) in ctx.author.roles and not ctx.guild.get_role(1071476455348903977) in ctx.author.roles:
        await ctx.send(embed=authority_error())
        return

    if arg == None:
        await ctx.send(embed=vote_error("引数が指定されていません！"))
        return

    elif arg == "create":
        try:
            if channel == None:
                await ctx.send(embed=vote_create_error("送信先のテキストチャンネルIDが指定されていません！"))
                return
            if len(args) == 0:
                await ctx.send(embed=vote_create_error("投票タイトルが指定されていません！"))
                return
            elif len(args) == 1:
                await ctx.send(embed=vote_create_error("選択肢が指定されていません！"))
                return
            vote_title = args[0]
            vote_mes = ""
            vote_icon = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                         "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
            for i in range(len(args[1:])):
                vote_mes += f"{vote_icon[i]} {args[i+1]}\t：\n"
            message = await ctx.send(f"【投票受付中】`(バグったらリサイクルマークを押してください)`\n"
                                     f"**{vote_title}**\n"
                                     f"\n"
                                     f"{vote_mes}")
            for i in range(len(args[1:])):
                await message.add_reaction(vote_icon[i])
            await message.add_reaction("♻️")
        except:
            await ctx.send

    elif arg == "role":
        pass

    else:
        await ctx.send(embed=vote_error("引数が違います！"))
        return


@client.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    line = message.content.split("\n")
    user = client.get_user(payload.user_id)
    user_name = user.name
    number = payload.emoji.name

    if line[0] == "【投票受付中】`(バグったらリサイクルマークを押してください)`":
        mes = []
        new_mes = ""
        reactions = message.reactions
        new_members = []
        i = 0
        if number == "♻️":  # リフレッシュ用。

            new = []
            for reaction_ in reactions:
                new.append([reaction_.emoji])
                async for user in reaction_.users():
                    if not user.bot:
                        new[i].append(user.name)
                i += 1
            for i in range(len(line)):
                mes.append(line[i].split(" "))
                for j in range(len(new)):
                    if mes[i][0] == new[j][0]:
                        try:
                            mes[i][2] = ""

                        except:
                            mes[i].append("")
                        for user_ in new[j][1:]:
                            mes[i][2] += f"{user_},　"
                        line[i] = f"{mes[i][0]} {mes[i][1]} {mes[i][2][:-2]}"
                new_mes += f"{line[i]}\n"
            await message.edit(content=new_mes)
            await message.remove_reaction('♻️', user)
            return

        for i in range(len(line)):
            mes.append(line[i].split(" "))
            if mes[i][0] == number:
                try:
                    mes[i][2] += f",　{user_name}"
                except:
                    mes[i].append(user_name)
                line[i] = f"{mes[i][0]} {mes[i][1]} {mes[i][2]}"
            new_mes += f"{line[i]}\n"
        await message.edit(content=new_mes)


@client.event
async def on_raw_reaction_remove(payload):

    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    line = message.content.split("\n")
    user = client.get_user(payload.user_id)
    user_name = user.name
    number = payload.emoji.name

    if line[0] == "【投票受付中】`(バグったらリサイクルマークを押してください)`":
        mes = []
        new_mes = ""
        new_members = ""
        for i in range(len(line)):
            mes.append(line[i].split(" "))
            if mes[i][0] == number:
                members = mes[i][2].split(",　")
                for j in range(len(members)):
                    if members[j] == user_name:
                        members[j] = ""
                    else:
                        new_members += f"{members[j]},　"
                mes[i][2] = new_members[:-2]
                if mes[i][2] == "":
                    line[i] = f"{mes[i][0]} {mes[i][1]}"
                else:
                    line[i] = f"{mes[i][0]} {mes[i][1]} {mes[i][2]}"
            new_mes += f"{line[i]}\n"
        await message.edit(content=new_mes)


"""
エラーメッセージ一覧
"""


def any_error(*ctx):
    embed = discord.Embed(
        title=f"*Error*：{ctx[0]}", description=f"{ctx[1]}", color=0xff0000)
    return embed


def authority_error():
    embed = discord.Embed(
        title=f"*Error*：実行権限がありません！", description="このコマンドを実行するには権限が必要です。", color=0xff0000)
    return embed


def vote_error(ctx):
    embed = discord.Embed(
        title=f"*Error*：{ctx}", description="以下の様式で記述してください。\n```\n!vote create [テキストチャンネルID] [投票タイトル] [投票先1] [投票先2] ...\n\n!vote role [テキストチャンネルID] [テキストメッセージID] [選択肢の番号] [ロール] ...```\n詳細：https://github.com/kariumi/ITCBot2023", color=0xff0000)
    return embed


def vote_create_error(ctx):
    embed = discord.Embed(
        title=f"*Error*：{ctx}", description="以下の様式で記述してください。\n```\n!vote create [テキストチャンネルID] [投票タイトル] [投票先1] [投票先2] ...\n```\n詳細：https://github.com/kariumi/ITCBot2023", color=0xff0000)
    return embed


token = getenv('DISCORD_BOT_TOKEN')
client.run(token)
