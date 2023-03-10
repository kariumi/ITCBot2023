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
import asyncio


class color:
    RED = '\033[31m'  # (文字)赤
    GREEN = '\033[32m'  # (文字)緑
    YELLOW = '\033[33m'  # (文字)黄
    BLUE = '\033[34m'  # (文字)青
    MAGENTA = '\033[35m'  # (文字)マゼンタ
    CYAN = '\033[36m'  # (文字)シアン
    WHITE = '\033[37m'  # (文字)白
    BOLD = '\033[1m'  # 太字
    UNDERLINE = '\033[4m'  # 下線
    INVISIBLE = '\033[08m'  # 不可視
    REVERCE = '\033[07m'  # 文字色と背景色を反転
    BG_RED = '\033[41m'  # (背景)赤
    BG_GREEN = '\033[42m'  # (背景)緑
    BG_YELLOW = '\033[43m'  # (背景)黄
    BG_BLUE = '\033[44m'  # (背景)青
    BG_MAGENTA = '\033[45m'  # (背景)マゼンタ
    BG_CYAN = '\033[46m'  # (背景)シアン
    BG_WHITE = '\033[47m'  # (背景)白
    RESET = '\033[0m'  # 全てリセット


intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

authority_role = ["", ""]

utc = datetime.timezone.utc


@client.event
async def on_ready():
    print(f"{color.YELLOW}{client.user}{color.RESET}でログインしました")
    Trial_entry_explulsion.start()


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send(embed=any_error("指定したチャンネルが見つかりません"))
    elif isinstance(error, commands.CommandNotFound):
        return
    raise error


"""
一時的に作ったやつ
"""


@client.command()
async def remove(ctx):
    await ctx.send(content="1 1")
    print("aaa")


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
    authority = authority_check(ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog("!shuffle : Error00")
        return
    if ctx.author.voice is None:
        await ctx.send(embed=any_error("ボイスチャンネルに入ってください", ""))
        printLog("!shuffle : Error01")
        return
    if len(channels) == 0:
        await ctx.send(embed=any_error("ボイスチャンネルを指定してください", ""))
        printLog("!shuffle : Error02")
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

    await printLog(f"{channel.mention}に接続している人を移動させました")

"""
!vote
投票を作成して色々できる

!vote create [テキストチャンネルID] [投票タイトル] [投票先1] [投票先2] [投票先3] ...
投票を作成してくれます。

!vote role [テキストチャンネルID] [テキストメッセージID] [投票番号] [ロール]
ロールを付与できます。

"""

# 拡張性を高くしようと思ってたら変に複雑になってしまった
# 特に引数が分かりにくい


@client.command()
async def vote(ctx, arg=None, channel: typing.Optional[TextChannel] = None, * args):
    authority = authority_check(ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog("!vote : Error00")
        return

    if arg == None:
        await ctx.send(embed=vote_error("引数が指定されていません！"))
        await printLog("!vote : Error01")
        return

    elif arg == "create":
        if channel == None:
            await ctx.send(embed=vote_create_error("送信先のテキストチャンネルIDが指定されていません！"))
            await printLog("!vote : Error02")
            return
        if len(args) == 0:
            await ctx.send(embed=vote_create_error("投票タイトルが指定されていません！"))
            await printLog("!vote : Error03")
            return
        elif len(args) == 1:
            await ctx.send(embed=vote_create_error("選択肢が指定されていません！"))
            await printLog("!vote : Error04")
            return
        elif len(args) > 10:
            await ctx.send(embed=vote_create_error("選択肢が多すぎます！最大9個まで指定できます。"))
            await printLog("!vote : Error05")
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

    elif arg == "finish":

        message = await channel.fetch_message(int(args[0]))
        for embed in message.embeds:
            description_ = embed.description
        title = "【投票終了】`(バグっている場合はリサイクルマークを押してください)`"
        embed = discord.Embed(
            title=f"{title}", description=description_, color=0x191970)
        await message.edit(embed=embed)

    else:
        await ctx.send(embed=vote_error("引数が違います！"))
        await printLog("!vote : Error06")
        return


"""
!get_date [ロール]
指定ロールに所属しているメンバーのサーバー参加日/その日からの経過日数を教えてくれる。
体験入部の管理用に作ったけどそっちは自動でやってくれるので手動で実行することはほぼない。

"""


@client.command()
async def get_date(ctx, role: typing.Optional[Role] = None):

    if role == None:
        await ctx.send(embed=get_date_error("ロールが指定されていません！"))
        await printLog("!get_date : Error01")
        return

    now_time = datetime.datetime.now(tz=utc)  # 現在時刻を取得

    message = f"__{role.mention}の一覧:{now_time.year}/{now_time.month}/{now_time.day} {now_time.hour}:{now_time.minute}\n__\n__参加日\t\t経過日数\t名前__\n"

    sorted_taiken_members = sorted(
        role.members, key=lambda x: x.joined_at)  # 参加日順にソート

    for member in sorted_taiken_members:
        # ログ用
        member_days = now_time - member.joined_at
        message += f"{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日\t{member.name}\n"

    await ctx.send(message)  # ログ


"""

!vote_role
ロールを割り振る用の投票を作成。自動でロールを割り振ることが出来ます。
"""


@client.command()
async def vote_role(ctx, channel: typing.Optional[TextChannel] = None, title="", *roles: typing.Optional[Role]):
    authority = authority_check(ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog("!vote_role : Error00")
        return
    if channel == None:
        await ctx.send(embed=set_role_error("テキストチャンネルが指定されていません。"))
        await printLog("!vote_role : Error01")
        return
    if title == "":
        await ctx.send(embed=set_role_error("タイトルが指定されていません。"))
        await printLog("!vote_role : Error02")
        return
    if len(roles) == 0:
        await ctx.send(embed=set_role_error("roleが指定されていません。"))
        await printLog("!vote_role : Error03")
        return
    message = f"**{title}**\n\n"
    vote_icon = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                 "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    for i in range(len(roles)):
        message += f"{vote_icon[i]} {roles[i].name}\n"
    message += f"😎 選択をやり直す"
    embed = discord.Embed(
        color=0x0000ff, title="【投票受付中】ロールが自動で付与されます。", description=message)
    id = await channel.send(embed=embed)
    for i in range(len(roles)):
        await id.add_reaction(vote_icon[i])
    await id.add_reaction("😎")


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
    for embed in embeds:  # embedを使用している場合はこの中を使用する。

        title = embed.title
        line = embed.description.split("\n")
        user = client.get_user(payload.user_id)
        user_name = user.name
        number = payload.emoji.name

        # voteコマンド
        # 1.リフレッシュマークが押された時
        # 2.選択肢が押された時
        # 3.vote finish後にリフレッシュしたいとき（これはvote finishに統合すると一番良い。面倒くさいからやらん）
        # 4.vote finish後に選択肢が押された時
        if title == "【投票受付中】`(バグったらリサイクルマークを押してください)`":
            mes = []
            new_mes = ""
            reactions = message.reactions
            new_members = []
            i = 0
            # 1.リフレッシュマークが押された時
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
            # 2.選択肢が押された時
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
            return
        # 3.vote finish後にリフレッシュしたいとき（これはvote finishに統合すると一番良い。面倒くさいからやらん）
        if title == "【投票終了】`(バグっている場合はリサイクルマークを押してください)`":
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
            # 4.vote finish後に選択肢が押された時
            await message.remove_reaction(number, user)

        # vote_roleコマンド
        # 1.リセットボタンが押されたら選択肢にあるロールを全て剥奪
        # 2.押された選択肢に対応するロールを付与
        if title == "【投票受付中】ロールが自動で付与されます。":
            mes = []
            print(number)
            if number == "😎":   # ←絵文字が見えない（泣）フォントの問題かな
                vote_icon = ["1️⃣", "2️⃣", "3️⃣", "4️⃣",
                             "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
                vote_list = []
                for i in range(len(line)):
                    mes.append(line[i].split(" "))
                    for j in vote_icon:
                        if mes[i][0] == j:
                            vote_list.append(mes[i][1])
                guild = client.get_guild(payload.guild_id)
                print(vote_list)
                for role_name in vote_list:
                    role = discord.utils.get(guild.roles, name=role_name)
                    await payload.member.remove_roles(role)
                await message.remove_reaction(number, user)
                return
            else:
                for i in range(len(line)):
                    mes.append(line[i].split(" "))
                    if mes[i][0] == number:
                        guild = client.get_guild(payload.guild_id)
                        role = discord.utils.get(guild.roles, name=mes[i][1])
                        await message.remove_reaction(number, user)
                        await payload.member.add_roles(role)
                return

    #
    # 新歓サーバー用
    # スタンプを押されたら
    #

    # CG

    CGch = client.get_channel(1056757946610110494)
    PROGch = client.get_channel(1056760188243292273)
    DTMch = client.get_channel(1056758114600353922)
    MVch = client.get_channel(1056758410558845038)

    user = client.get_user(payload.user_id)
    stamp = payload.emoji.name

    if payload.message_id == 1076845241421803530:
        await message.remove_reaction(stamp, user)
        await payload.member.move_to(CGch)

    if payload.message_id == 1076845246501093466:
        await message.remove_reaction(stamp, user)
        await payload.member.move_to(PROGch)

    if payload.message_id == 1076845256970092564:
        await message.remove_reaction(stamp, user)
        await payload.member.move_to(DTMch)

    if payload.message_id == 1076845260975652955:
        await message.remove_reaction(stamp, user)
        await payload.member.move_to(MVch)


"""
DMを受け取ったときの処理（TwitterのDMみたいなシステムで相互に返信可）

"""


@client.listen()
async def on_message(message):
    if message.author == client.user:
        return

    # DMを管理するサーバー
    guild = client.get_guild(1075592226534600755)

    # 本鯖
    itcGuild = client.get_guild(377392053182660609)

    # DMカテゴリーの取得
    DMcategory = client.get_channel(1076657448200458362)

    # test送信用のtextchannel
    test_channel = client.get_channel(1075592227180527699)

    # DMを受け取る→データベースに送信　完成　バグなし
    if type(message.channel) == discord.DMChannel:
        database = await client.get_channel(1076661281131601940).fetch_message(1076864300200755261)
        data_ = database.content.split("\n")
        for i in data_:
            data = i.split(" ")
            if int(data[0]) == message.author.id:
                sendMes = await client.get_channel(int(data[1])).send(message.content)
                await printLog(f"BOTが{message.author.name}からDMを受け取りました。\n{sendMes.jump_url}")
                return
        # 初めて送ってきた人はチャンネルを作成する
        channel = await guild.create_text_channel(message.author.name, category=DMcategory)
        send_Mes = await client.get_channel(channel.id).send(f"【{message.author.name}】\n\n{message.content}")
        new_database = f"{database.content}"
        new_database += f"\n{message.author.id} {channel.id}"
        await database.edit(content=new_database)
        await printLog(f"BOTが{message.author.name}からDMを初めて受け取りました。\n{sendMes.jump_url}\nDBに{message.author.name}を追加します。\n{database.jump_url}")
        return
    # データベースに受け取る→DM送信　完成　バグなし
    if message.channel.category == DMcategory:
        database = await client.get_channel(1076661281131601940).fetch_message(1076864300200755261)
        data_ = database.content.split("\n")
        for i in data_:
            data = i.split(" ")
            if int(data[1]) == message.channel.id:
                member = itcGuild.get_member(int(data[0]))
                await member.send(message.content)
                await printLog(f"BOTから、{member.name}にDMを返信しました。\n{message.jump_url}")
                return

    # ロール一斉送信　完成済み　バグなし

    RoleCaregory = client.get_channel(1076860376924307557)

    if message.channel.category == RoleCaregory:
        await printLog(message.channel.topic)
        try:
            role = itcGuild.get_role(int(message.channel.topic))
            await printLog(f"以下の文章を@{role.name}ロール保持者に一斉送信します。")

            members = role.members
            for member in members:
                await member.send(message.content)
                await printLog(f"|{member.name}に送信しました。")
        except:
            await printLog("DM一斉送信に失敗しました。")

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
        if title == "【投票終了】`(バグっている場合はリサイクルマークを押してください)`":
            await message.remove_reaction(number, user)


"""
体験入部生が60日/90日経過したらお知らせする。
（予定では、botが自動で60日経過でDMを送信し、90日でkickする。）
毎日のログはDB鯖のbot-logに送信します。
60日が経過すると@体験入部のロールを外し、@要確認をつける。
90日が経過すると、代表にDMを送信する。
"""


# ループが実行される時間(UTC)
time = datetime.time(hour=15, minute=0, tzinfo=utc)


@tasks.loop(time=time)
async def Trial_entry_explulsion():

    # itcの鯖
    ITCserver = client.get_guild(1075592226534600755)
    # 代表の人を取得
    member_leader = ITCserver.get_member(588717978594443264)
    # ｵﾚ
    member_me = ITCserver.get_member(599515603484672002)
    # 体験入部ロール
    taiken_role = ITCserver.get_role(851748635023769630)
    # 要確認ロール
    yo_kakunin_role = ITCserver.get_role(833323166440095744)

    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now_time = datetime.datetime.now(JST)  # 現在時刻を取得
    now = now_time.strftime('%Y/%m/%d %H:%M:%S')
    role = client.get_guild(377392053182660609).get_role(851748635023769630)
    # ↓↓year=は毎年変更する必要あり。↓↓
    time_start_date = datetime.datetime(year=2023, month=4, day=1, tzinfo=utc)
    message = f"__{role.mention}の一覧を出力します:\n参加日\t経過日数\t名前__\n"

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

        if member_days.days == 60:  # 60
            # 体験入部ロールを外し、要確認ロールを付与
            member.remove_roles(taiken_role)
            member.add_roles(yo_kakunin_role)
            day60_members.append(member.name)
            message += f"__***❗\t{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日***\t{member.mention}__\n"
        elif 60 < member_days.days < 90:
            message += f"_{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日\t{member.mention}_\n"

        elif member_days.days >= 90:  # 90~<----------------ここを変更すること！！！！
            day90_members.append(member.name)
            message += f"__***❌{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日***__\t{member.mention}\n"
        elif member_days.days >= 0:  # 0~59,61~89
            message += f"{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日\t{member.name}\n"

    if len(day60_members) > 0 or len(day90_members) > 0:
        leader_role = client.get_guild(
            377392053182660609).get_role(377446484162904065)

    if len(day60_members) > 0:
        message += f"60日を超えたメンバーが{len(day60_members)}人いました。\n"
    else:
        message += "60日を超えたメンバーはいませんでした。\n"

    # 代表に送信するDMの内容
    if len(day90_members) > 0:
        dm_mes = "90日を超えたメンバーを検出しました。確認してください。\n"
        message += f"90日を超えたメンバーが{len(day90_members)}人いました。\n"
        for i in range(len(day90_members)):
            dm_mes += f"{member.name}\t【参加日】{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t【経過日数】{member_days.days}日\n"
        await member_me.send(dm_mes)  # テスト用に自分にも送信する。後で消してよい。
        await member_leader.send(dm_mes)
    else:
        message += "90日を超えたメンバーはいませんでした。\n"

    await printLog(message)  # ログを出力


"""
@体験入部のロールが付与された時、その人にBOTから自動でDMを送信する
"""


@client.event
async def on_member_update(before, after):
    if before.guild.id == 377392053182660609:
        guild = client.get_guild(377392053182660609)
        role = guild.get_role(851748635023769630)  # 体験入部

        # 送信する文章の取得
        teikeibunCh = client.get_channel(1076714278154932344)
        sendMes = await teikeibunCh.fetch_message(1076714411512840192)

        # roleの差分を取得
        # diff_role = list(set(before.roles) ^ set(after.roles))
        # await printLog(f"{before.name}の{diff_role}ロールが変更されました。")
        if (not (role in before.roles)) and (role in after.roles):
            try:
                await before.send(sendMes.content)
                await printLog(f"{before.name}に「体験入部が付与された時」のDMを送信しました。")
            except:  # 失敗したら報告
                await printLog(f"Error!!：{before.name}に「体験入部が付与された時」のDMを送信できませんでした。")
            return


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


def set_role_error(ctx):
    embed = discord.Embed(
        title=f"*Error*：{ctx}", description="以下の様式で記述してください。\n```\n!set_tole [テキストチャンネルID] [ロール] ...\n```\n詳細：https://github.com/kariumi/ITCBot2023", color=0xff0000)
    return embed


"""
権限の確認
"""


def authority_check(ctx):
    true_role = [968160313797136414, 1051495123285983304, 1052290950875062403]
    # true_guildはtrue_roleと一対一対応で。
    true_guild = [884771781708247041, 1053669243616501800]

    authority = False

    # サーバー内ロール権限
    try:
        for i in range(len(true_role)):
            if ctx.guild.get_role(true_role[i]) in ctx.author.roles:
                authority = True
    except:
        pass
    try:
        for i in range(len(true_guild)):
            if ctx.guild == client.get_guild(true_guild[i]):
                authority = True
    except:
        pass
    return authority


"""
ログを残す
printLog
"""


async def printLog(content):
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    nowTime = datetime.datetime.now(JST)
    textch = client.get_channel(1076682589185790065)
    now = nowTime.strftime('%Y/%m/%d %H:%M:%S')
    await textch.send(f"[{now}] - {content}")

token = getenv('DISCORD_BOT_TOKEN')
client.run(token)
