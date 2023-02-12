import datetime
import discord
import traceback
from discord.ext import tasks, commands
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

utc = datetime.timezone.utc


@client.event
async def on_ready():
    print(f"{client.user}でログインしました")
    Trial_entry_explulsion.start()


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
        message_contents = (f"**{vote_title}**\n"
                            f"\n"
                            f"{vote_mes}")
        embed = discord.Embed(
            title=f"【投票受付中】`(バグったらリサイクルマークを押してください)`", description=f"{message_contents}", color=0x0000ff)
        message = await channel.send(embed=embed)
        for i in range(len(args[1:])):
            await message.add_reaction(vote_icon[i])
        await message.add_reaction("♻️")

    elif arg == "role":
        pass

    else:
        await ctx.send(embed=vote_error("引数が違います！"))
        return

"""
!get_date [ロール]
指定ロールに所属しているメンバーのサーバー参加日/その日からの経過日数を教えてくれる。
体験入部の管理用に作ったけどそっちは自動でやってくれるので手動で実行することはほぼない。

"""


@client.command()
async def get_date(ctx, role: typing.Optional[Role] = None):
    if not ctx.guild.get_role(968160313797136414) in ctx.author.roles and not ctx.guild.get_role(1071476455348903977) in ctx.author.roles:
        await ctx.send(embed=authority_error())
        return
    if role == None:
        await ctx.send(embed=get_date_error("ロールが指定されていません！"))
        return

    now_time = datetime.datetime.now(tz=utc)  # 現在時刻を取得

    message = f"__{role.mention}の一覧:{now_time.year}/{now_time.month}/{now_time.day} {now_time.hour}:{now_time.minute}\n__\n__参加日\t経過日数\t名前__\n"

    day90_members = []
    day60_members = []
    sorted_taiken_members = sorted(
        role.members, key=lambda x: x.joined_at)  # 参加日順にソート

    for member in sorted_taiken_members:
        # ログ用
        member_days = now_time - member.joined_at
        message += f"\t{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日\t{member.name}\n"

    await ctx.send(message)  # ログ


"""
（制作中）
!set_role
ロールを割り振る。
"""


@client.command()
async def set_role(ctx, channel: typing.Optional[TextChannel] = None):
    if not ctx.guild.get_role(968160313797136414) in ctx.author.roles and not ctx.guild.get_role(1071476455348903977) in ctx.author.roles:
        await ctx.send(embed=authority_error())
        return
    embed = discord.Embed(color=0xc0ffee, title="ロール割振", description="テストです。\n"
                          "prog部 : :computer:\n"
                          "cg部   : :art:\n"
                          "dtm部  : :headphones:\n"
                          "mv部   : :movie_camera:"
                          )
    message = await ctx.send(embed=embed)
    await message.add_reaction("💻")
    await message.add_reaction("🎨")
    await message.add_reaction("🎧")
    await message.add_reaction("🎥")
    if ctx.channel != 377392053182660609:
        await ctx.send("このコマンドはITCサーバー以外では使用できません。")
        return

"""
on_raw_reaction_add

- voteコマンドで使用
    - 投票にリアクションが押されたらメンバーリストを更新
    - リフレッシュマークでバグを自動修正
- set_roleで使用
    - メッセージにリアクションを押されたらロールを付与
"""


@client.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return

    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    embeds = message.embeds
    for embed in embeds:

        title = embed.title
        line = embed.description.split("\n")
        user = client.get_user(payload.user_id)
        user_name = user.name
        number = payload.emoji.name

        if title == "【投票受付中】`(バグったらリサイクルマークを押してください)`":
            mes = []
            new_mes = ""
            reactions = message.reactions
            new_members = []
            i = 0
            if number == "♻️":  # リフレッシュ用。
                temp_embed = embed
                temp_embed.color = 0xffff00
                await message.edit(embed=temp_embed, content="⚠️⚠️__***ボタンを押さないでください***__⚠️⚠️")

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
                embed = discord.Embed(
                    title=f"{title}", description=f"{new_mes}", color=0x008000)
                await message.edit(embed=embed, content="♻️__***リフレッシュ完了！***__♻️")

                if not user.bot:
                    await message.remove_reaction('♻️', user)
                embed.color = 0x0000ff
                await message.edit(embed=embed, content="")
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
                embed = discord.Embed(
                    title=f"{title}", description=f"{new_mes}", color=0x0000ff)
            await message.edit(embed=embed)

# set_role用↓
    if payload.member.bot:
        return
    for embed in await client.get_channel(payload.channel_id).fetch_message(payload.message_id).embeds:
        if embed.title == "ロール割振":
            guild = client.get_guild(payload.guild_id)
            await payload.member.add_roles(guild.get_role(851748635023769630))
            # 体験入部付与
            if payload.emoji.name == "💻":
                await payload.member.add_roles(guild.get_role(837510590841880617))
            if payload.emoji.name == "🎨":
                await payload.member.add_roles(guild.get_role(829263508016463923))
            if payload.emoji.name == "🎧":
                await payload.member.add_roles(guild.get_role(837510593077706782))
            if payload.emoji.name == "🎥":
                await payload.member.add_roles(guild.get_role(837510944459456562))

"""
on_raw_reaction_remove

- voteコマンド
    - リアクションを外されたらメンバーリストを更新

"""


@client.event
async def on_raw_reaction_remove(payload):

    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    embeds = message.embeds
    for embed in embeds:
        title = embed.title
        line = embed.description.split("\n")
        user = client.get_user(payload.user_id)
        user_name = user.name
        number = payload.emoji.name

        if title == "【投票受付中】`(バグったらリサイクルマークを押してください)`":
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
            embed = discord.Embed(
                title=f"{title}", description=f"{new_mes}", color=0x0000ff)
            await message.edit(embed=embed)


"""
体験入部生が60日/90日経過したらお知らせする。
（予定では、botが自動で60日経過でDMを送信し、90日でkickする。）
現段階では、サーバー参加日から何日経過したかを視覚的に分かりやすく表示してくれるだけ。
"""


# ループが実行される時間(UTC)
time = datetime.time(hour=15, minute=0, tzinfo=utc)


@tasks.loop(time=time)
async def Trial_entry_explulsion():
    now_time = datetime.datetime.now(tz=utc)  # 現在時刻を取得
    role = client.get_guild(377392053182660609).get_role(851748635023769630)
    text_ch = client.get_channel(829334489473482752)
    # ↓↓year=は毎年変更する必要あり。↓↓
    time_start_date = datetime.datetime(year=2020, month=4, day=1, tzinfo=utc)
    message = f"__{role.mention}の一覧:{now_time.year}/{now_time.month}/{now_time.day} {now_time.hour}:{now_time.minute}現在\n__経過日数について、4月1日以前の参加者は4月1日から計算する。\n\n__参加日\t経過日数\t名前__\n"

    day90_members = []
    day60_members = []
    sorted_taiken_members = sorted(
        role.members, key=lambda x: x.joined_at)  # 参加日順にソート

    for member in sorted_taiken_members:  # 90日、60日経過メンバーを絞る->90_members、60_membersへ。尚、4月1日以前に参加した者は4月1日参加とみなして計算する。

        if member.joined_at > time_start_date:
            member_days = now_time - member.joined_at
        else:
            member_days = now_time - time_start_date
        # ログ用

        if member_days.days == 60:
            day60_members.append(member.name)
            message += f"__***❗\t{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日***\t{member.mention}__\n"
        elif member_days.days == 70:
            day90_members.append(member.name)
            message += f"__***❌\t{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日***__\t{member.mention}\n"
        elif member_days.days >= 0:
            message += f"\t{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日\t{member.name}\n"
        else:
            message += f"\t{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t0日\t{member.name}\n"
    if day60_members > 0 or day90_members > 0:
        leader_role = client.get_guild(
            377392053182660609).get_role(377446484162904065)
        message += f"{leader_role.mention}:2ヶ月/3ヶ月経過したメンバーがいます。対応してください。"

    await text_ch.send(message)  # ログとして出力


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


def get_date_error(ctx):
    embed = discord.Embed(
        title=f"*Error*：{ctx}", description="以下の様式で記述してください。\n```\n!get_date [ロール] ...\n```\n詳細：https://github.com/kariumi/ITCBot2023", color=0xff0000)
    return embed


"""
権限の確認
"""


def authority_check(ctx):
    pass


token = getenv('DISCORD_BOT_TOKEN')
client.run(token)
