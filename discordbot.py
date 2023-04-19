import datetime
import discord
import traceback
from discord.ext import tasks, commands
from os import getenv
import random
import typing
import sqlite3
from discord import TextChannel, VoiceChannel, Role, Intents, app_commands
import asyncio
import csv
import pprint
import sys
import linecache
import time
# from git import *
from extensions.utils.bot_error import *
from extensions.utils.others import *
#a
final_update = get_startup_jst()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

authority_role = ["", ""]


def failure(e):
    exc_type, exc_obj, tb = sys.exc_info()
    lineno = tb.tb_lineno
    mes = (str(lineno) + ":" + str(type(e)))
    return mes


@client.event
async def on_ready():
    print(f"{color.YELLOW}{client.user}{color.RESET}でログインしました")
    await client.tree.sync()
    await printLog(client, final_update)
    Trial_entry_explulsion.start()


@client.event
async def setup_hook():
    await client.load_extension("extensions.ping")
    await client.load_extension("extensions.get_date")
    await client.load_extension("extensions.shuffle")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send(embed=any_error("指定したチャンネルが見つかりません"))
    elif isinstance(error, commands.CommandNotFound):
        return
    raise error

"""
urlを送信したときに、urlからギルドID、チャンネルID、メッセージIDを分離してくれるやつのテスト
"""


@client.hybrid_command()
async def url(ctx, url_):
    try:
        id_name = ["鯖ID", "チャンネルID", "メッセージID"]
        separated_url = separate_URL(url_)
        message = "分離しました！\n"
        for i in range(len(separated_url)):
            message += f"{id_name[i]}:{separated_url[i]}\n"
        await printLog(client, message)
    except Exception as e:
        await printLog(client, failure(e))


"""
!bot_mes
ボットから好きなチャンネルに送信
"""
#このコメントは消して下さい

@client.hybrid_command(description = "(管理者のみ)")
async def bot_mes(ctx, textchannel: typing.Optional[TextChannel], arg):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    await textchannel.send(arg)


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
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote : Error00")
        return

    if arg == None:
        await ctx.send(embed=vote_error("引数が指定されていません！"))
        await printLog(client, "!vote : Error01")
        return

    elif arg == "create":
        if channel == None:
            await ctx.send(embed=vote_create_error("送信先のテキストチャンネルIDが指定されていません！"))
            await printLog(client, "!vote : Error02")
            return
        if len(args) == 0:
            await ctx.send(embed=vote_create_error("投票タイトルが指定されていません！"))
            await printLog(client, "!vote : Error03")
            return
        elif len(args) == 1:
            await ctx.send(embed=vote_create_error("選択肢が指定されていません！"))
            await printLog(client, "!vote : Error04")
            return
        elif len(args) > 10:
            await ctx.send(embed=vote_create_error("選択肢が多すぎます！最大9個まで指定できます。"))
            await printLog(client, "!vote : Error05")
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
        await printLog(client, "!vote : Error06")
        return

# """
# ロール一斉送信用チャンネル作成

# """


# @client.command()
# async def チャンネル一斉作成(ctx):
#     try:
#         isseisousin_category = client.get_channel(1076860376924307557)
#         db = client.get_guild(1075592226534600755)

#         itc = client.get_guild(377392053182660609)
#         roles = itc.roles
#         for role in roles:
#             try:
#                 await db.create_text_channel(f"{role.name}", category=isseisousin_category, topic=f"{role.id}")
#                 await printLog(client, f"{role.name} - 成功")
#             except:
#                 await printLog(client, f"{role.name}のチャンネルの作成に失敗しました")
#     except Exception as e:
#         await printLog(client, failure(e))
#a


"""
!taimen_list
対面部会に出席する人のリスト
"""
@client.hybrid_command(descrinption = "(管理者のみ)リスト作成") 
async def taimen_list(ctx,url,emoji_):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    try:
        urls=separate_URL(url)
        guild=client.get_guild(int(urls[0]))
        ch=client.get_channel(int(urls[1]))
        mes=await ch.fetch_message(int(urls[2]))
        
        reactions = mes.reactions
        for reaction in reactions:
            if reaction.emoji==emoji_:
                
                users=[user async for user in reaction.users()]
                dtm=[]
                cg=[]
                prog=[]
                mv=[]
                message=""
                dtm_role=guild.get_role(837510593077706782)
                dtm_t_role=guild.get_role(1093911788929683506)
                cg_role=guild.get_role(829263508016463923)
                cg_t_role=guild.get_role(1093911494518898889)
                prog_role=guild.get_role(837510590841880617)
                prog_t_role=guild.get_role(1093911704510931104)
                mv_role=guild.get_role(837510944459456562)
                mv_t_role=guild.get_role(1093911834270105620)
                message="参加表明している部員の一覧\n"
                for user in users:
                    time.sleep(0.1)
                    if dtm_role in user.roles:
                        dtm.append(user)
                    elif dtm_t_role in user.roles:
                        dtm.append(user)
                        
                    if cg_role in user.roles:
                        cg.append(user)
                    elif cg_t_role in user.roles:
                        cg.append(user)
                        
                    if prog_role in user.roles:
                        prog.append(user)
                    elif prog_t_role in user.roles:
                        prog.append(user)
                        
                    if mv_role in user.roles:
                        mv.append(user)
                    elif mv_t_role in user.roles:
                        mv.append(user)
                        
                    message+=f"{user.mention}\n"
                    
                message+="-----------------------------------------------------\n"
                await printLog(client,message) #参加表明している部員の一覧
                
                message="CGのメンバー\n"
                for user in cg:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await printLog(client,message)
                
                message="DTMのメンバー\n"
                for user in dtm:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await printLog(client,message)
                
                message="PROGのメンバー\n"
                for user in prog:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await printLog(client,message)
                
                message="MVのメンバー\n"
                for user in mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await printLog(client,message)

                    
    except Exception as e:
        await printLog(client,failure(e))
        
"""
!taimen_list
対面部会に出席する人のリスト、兼部とか全部出す
"""
@client.hybrid_command(descrinption = "(管理者のみ)リスト作成") 
async def taimen_list_all(ctx,url,emoji_):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    try:
        urls=separate_URL(url)
        guild=client.get_guild(int(urls[0]))
        ch=client.get_channel(int(urls[1]))
        mes=await ch.fetch_message(int(urls[2]))
        
        reactions = mes.reactions
        for reaction in reactions:
            if reaction.emoji==emoji_:
                
                users=[user async for user in reaction.users()]
                cg=[]
                dtm=[]
                prog=[]
                mv=[]
                cg_dtm=[]
                cg_prog=[]
                cg_mv=[]
                dtm_prog=[]
                dtm_mv=[]
                prog_mv=[]
                cg_dtm_prog=[]
                cg_dtm_mv=[]
                cg_prog_mv=[]
                dtm_prog_mv=[]
                cg_dtm_prog_mv=[]
                
                message=""
                dtm_role=guild.get_role(837510593077706782)
                dtm_t_role=guild.get_role(1093911788929683506)
                cg_role=guild.get_role(829263508016463923)
                cg_t_role=guild.get_role(1093911494518898889)
                prog_role=guild.get_role(837510590841880617)
                prog_t_role=guild.get_role(1093911704510931104)
                mv_role=guild.get_role(837510944459456562)
                mv_t_role=guild.get_role(1093911834270105620)
                #message="参加表明している部員の一覧\n"
                for user in users:
                    time.sleep(0.1)
                    
                        
                    if (cg_role in user.roles) and not(dtm_role in user.roles) and not (prog_role in user.roles) and not (mv_role in user.roles):
                        cg.append(user)
                    elif (cg_t_role in user.roles) and not(dtm_t_role in user.roles) and not (prog_t_role in user.roles) and not (mv_t_role in user.roles):
                        cg.append(user)
                    
                    if not (cg_role in user.roles) and (dtm_role in user.roles) and not (prog_role in user.roles) and not (mv_role in user.roles):
                        dtm.append(user)
                    elif not (cg_t_role in user.roles) and (dtm_t_role in user.roles) and not (prog_t_role in user.roles) and not (mv_t_role in user.roles):
                        dtm.append(user)
                        
                    if not (cg_role in user.roles) and not(dtm_role in user.roles) and  (prog_role in user.roles) and not (mv_role in user.roles):
                        prog.append(user)
                    elif not (cg_t_role in user.roles) and not (dtm_t_role in user.roles) and  (prog_t_role in user.roles) and not (mv_t_role in user.roles):
                        prog.append(user)
                        
                    if not (cg_role in user.roles) and not(dtm_role in user.roles) and not (prog_role in user.roles) and (mv_role in user.roles):
                        mv.append(user)
                    elif not (cg_t_role in user.roles) and not (dtm_t_role in user.roles) and not (prog_t_role in user.roles) and  (mv_t_role in user.roles):
                        mv.append(user)
                    
                    #2つ兼部
                    if (cg_role in user.roles) and (dtm_role in user.roles) and not (prog_role in user.roles) and not (mv_role in user.roles):
                        cg_dtm.append(user)
                    elif (cg_t_role in user.roles) and (dtm_t_role in user.roles) and not (prog_t_role in user.roles) and not (mv_t_role in user.roles):
                        cg_dtm.append(user)
                        
                    if  (cg_role in user.roles) and not(dtm_role in user.roles) and  (prog_role in user.roles) and not (mv_role in user.roles):
                        cg_prog.append(user)
                    elif  (cg_t_role in user.roles) and not (dtm_t_role in user.roles) and  (prog_t_role in user.roles) and not (mv_t_role in user.roles):
                        cg_prog.append(user)
                        
                    if  (cg_role in user.roles) and not(dtm_role in user.roles) and not (prog_role in user.roles) and  (mv_role in user.roles):
                        cg_mv.append(user)
                    elif  (cg_t_role in user.roles) and not (dtm_t_role in user.roles) and not (prog_t_role in user.roles) and  (mv_t_role in user.roles):
                        cg_mv.append(user)
                    
                    if not (cg_role in user.roles) and (dtm_role in user.roles) and  (prog_role in user.roles) and not (mv_role in user.roles):
                        dtm_prog.append(user)
                    elif not (cg_t_role in user.roles) and  (dtm_t_role in user.roles) and  (prog_t_role in user.roles) and not (mv_t_role in user.roles):
                        dtm_prog.append(user)
                    
                    if not (cg_role in user.roles) and (dtm_role in user.roles) and not (prog_role in user.roles) and  (mv_role in user.roles):
                        dtm_mv.append(user)
                    elif not (cg_t_role in user.roles) and  (dtm_t_role in user.roles) and not (prog_t_role in user.roles) and  (mv_t_role in user.roles):
                        dtm_mv.append(user)
                    
                    if not (cg_role in user.roles) and not(dtm_role in user.roles) and  (prog_role in user.roles) and  (mv_role in user.roles):
                        prog_mv.append(user)
                    elif not (cg_t_role in user.roles) and not (dtm_t_role in user.roles) and  (prog_t_role in user.roles) and  (mv_t_role in user.roles):
                        prog_mv.append(user)
                        
                    #3つ
                    if  (cg_role in user.roles) and (dtm_role in user.roles) and  (prog_role in user.roles) and not (mv_role in user.roles):
                        cg_dtm_prog.append(user)
                    elif  (cg_t_role in user.roles) and  (dtm_t_role in user.roles) and  (prog_t_role in user.roles) and not (mv_t_role in user.roles):
                        cg_dtm_prog.append(user)
                        
                    if  (cg_role in user.roles) and (dtm_role in user.roles) and not (prog_role in user.roles) and  (mv_role in user.roles):
                        cg_dtm_mv.append(user)
                    elif  (cg_t_role in user.roles) and (dtm_t_role in user.roles) and not (prog_t_role in user.roles) and  (mv_t_role in user.roles):
                        cg_dtm_mv.append(user)
                    
                    if  (cg_role in user.roles) and not(dtm_role in user.roles) and  (prog_role in user.roles) and  (mv_role in user.roles):
                        cg_prog_mv.append(user)
                    elif  (cg_t_role in user.roles) and not (dtm_t_role in user.roles) and  (prog_t_role in user.roles) and (mv_t_role in user.roles):
                        cg_prog_mv.append(user)
                    
                    if  not(cg_role in user.roles) and(dtm_role in user.roles) and  (prog_role in user.roles) and  (mv_role in user.roles):
                        dtm_prog_mv.append(user)
                    elif not (cg_t_role in user.roles) and (dtm_t_role in user.roles) and  (prog_t_role in user.roles) and (mv_t_role in user.roles):
                        dtm_prog_mv.append(user)
                    
                    #4つ
                    if  (cg_role in user.roles) and (dtm_role in user.roles) and  (prog_role in user.roles) and  (mv_role in user.roles):
                        cg_dtm_prog_mv.append(user)
                    elif  (cg_t_role in user.roles) and (dtm_t_role in user.roles) and  (prog_t_role in user.roles) and (mv_t_role in user.roles):
                        cg_dtm_prog_mv.append(user)
                        
                    message+=f"{user.mention}\n"
                    
                message+="-----------------------------------------------------\n"
                #await printLog(client,message) #参加表明している部員の一覧
                
                message="CGだけのメンバー\n"
                for user in cg:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="DTMだけのメンバー\n"
                for user in dtm:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="PROGだけのメンバー\n"
                for user in prog:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="MVだけのメンバー\n"
                for user in mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="CG&DTMのメンバー\n"
                for user in cg_dtm:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="CG&PROGのメンバー\n"
                for user in cg_prog:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="CG&MVのメンバー\n"
                for user in cg_mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="DTM&PROGのメンバー\n"
                for user in dtm_prog:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="DTM&MVのメンバー\n"
                for user in dtm_mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="PROG&MVのメンバー\n"
                for user in prog_mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="CG&DTM&PROGのメンバー\n"
                for user in cg_dtm_prog:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="CG&DTM&MVのメンバー\n"
                for user in cg_dtm_mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="CG&PROG&MVのメンバー\n"
                for user in cg_prog_mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="DTM&PROG&MVのメンバー\n"
                for user in dtm_prog_mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                
                message="CG&DTM&PROG&MVのメンバー\n"
                for user in cg_dtm_prog_mv:
                    message+=f"{user.mention}\n"
                message+="-----------------------------------------------------\n"
                await ctx.send(message)
                    
                    
    except Exception as e:
        await printLog(client,failure(e))


"""
!おみくじ
なんとなく
"""


@client.hybrid_command(name="おみくじ", description="今日の運勢を表示します！")
async def おみくじ(ctx):
    # img = ["daikichi.png", "kichi.png",
    #       "syoukichi.png", "kyou.png", "daikyou.png"]
    unsei = ["大吉 ❤️", "吉 🤍", "小吉 🤍", "凶 💙", "大凶 💙"]
    # daikichi_pool = ["今日であればあなたの思いが届くかもしれません…", "通帳見てみな！4630万円入金されてない？？"]
    # kichi_pool = ["お、100円玉拾った！", "財布に入ってるクーポン券、今日までだよ！"]
    # syoukichi_pool = ["う～ん、微妙！！", "課題やった？", "笑う門には福来る！笑吉！！(笑)"]
    # kyou_pool = ["え、、レポート課題忘れない？今日までだよ（絶望）", "こういう日もあるよ。。"]
    # daikyou_pool = ["多分、今日出かけたら終電逃すよ", "明日テストあるよ！！"]
    daikichi_pool = []
    kichi_pool = []
    syoukichi_pool = []
    kyou_pool = []
    daikyou_pool = []

    # luckyItem = ["龍角散", "理科大の水", "Apple Pencil", "四つ葉のクローバー", "虚無",
    #             "モバイルバッテリー", "正八面体", "バッグクロージャー", "バラン", "三角フラスコ", "Linux", "2000円札"]
    # luckyIMG = ["ryuukakusan.png", "rikadainomizu.png", "applePencil.png", "clover.png", "kyomu.png",
    #            "mobile_battery.png", "seihachimentai.png", "bag_closure.png", "baran.png", "flask.png", "linux.png", "2000yen.png"]
    luckyItem = []
    luckyIMG = []
    num = random.randrange(5)
    title = f"{unsei[num]}"
    with open('data/omikuji.csv') as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        f_T = [list(x) for x in zip(*l)]
        for data in f_T[1]:
            if data == "大吉":
                pass
            elif data == "":
                pass
            else:
                daikichi_pool.append(data)
        for data in f_T[2]:
            if data == "吉":
                pass
            elif data == "":
                pass
            else:
                kichi_pool.append(data)
        for data in f_T[3]:
            if data == "小吉":
                pass
            elif data == "":
                pass
            else:
                syoukichi_pool.append(data)
        for data in f_T[4]:
            if data == "凶":
                pass
            elif data == "":
                pass
            else:
                kyou_pool.append(data)
        for data in f_T[5]:
            if data == "大凶":
                pass
            elif data == "":
                pass
            else:
                daikyou_pool.append(data)
        for data in f_T[8]:
            if data == "ラッキーアイテムimg":
                pass
            elif data == "":
                pass
            else:
                luckyIMG.append(data)
        for data in f_T[7]:
            if data == "ラッキーアイテム":
                pass
            elif data == "":
                pass
            else:
                luckyItem.append(data)

    if num == 0:
        num2 = random.randrange(len(daikichi_pool))
        description_ = daikichi_pool[num2]
    elif num == 1:
        num2 = random.randrange(len(kichi_pool))
        description_ = kichi_pool[num2]
    elif num == 2:
        num2 = random.randrange(len(syoukichi_pool))
        description_ = syoukichi_pool[num2]
    elif num == 3:
        num2 = random.randrange(len(kyou_pool))
        description_ = kyou_pool[num2]
    elif num == 4:
        num2 = random.randrange(len(daikyou_pool))
        description_ = daikyou_pool[num2]
    embed = discord.Embed(
        title=f"{title}", description=description_, color=0xffffff)
    num3 = random.randrange(len(luckyIMG))
    avatar = ctx.message.author.avatar.url
    embed.set_author(
        name=f"{ctx.author.name}さんの今日の運勢は…", icon_url=avatar)
    embed.add_field(name="ラッキーアイテム", value=f"{luckyItem[num3]}")
    try:
        img_url = f"img/omikuji/luckyItem/{luckyIMG[num3]}"
        file = discord.File(fp=img_url, filename="img.png")
    except:
        img_url = f"img/omikuji/luckyItem/noImage.png"
        file = discord.File(fp=img_url, filename="img.png")
    embed.set_thumbnail(url="attachment://img.png")

    await ctx.send(embed=embed, file=file)


"""

!vote_role
ロールを割り振る用の投票を作成。自動でロールを割り振ることが出来ます。
"""


@client.command()
async def vote_role(ctx, channel: typing.Optional[TextChannel] = None, title="", *roles: typing.Optional[Role]):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    if channel == None:
        await ctx.send(embed=set_role_error("テキストチャンネルが指定されていません。"))
        await printLog(client, "!vote_role : Error01")
        return
    if title == "":
        await ctx.send(embed=set_role_error("タイトルが指定されていません。"))
        await printLog(client, "!vote_role : Error02")
        return
    if len(roles) == 0:
        await ctx.send(embed=set_role_error("roleが指定されていません。"))
        await printLog(client, "!vote_role : Error03")
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


@client.hybrid_command(name="乱数",description = "乱数生成")
@discord.app_commands.describe(min='最低値',max='最大値')
async def 乱数(ctx, min, max):
    await ctx.send(random.randint(int(min), int(max)))

"""
on_raw_reaction_add

- voteコマンドで使用
    - 投票にリアクションが押されたらメンバーリストを更新
    - リフレッシュマークでバグを自動修正
- set_roleで使用
    - メッセージにリアクションを押されたらロールを付与
"""


@ client.event
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


    #リアクションロック
    
    botguild=client.get_guild(1098052668431290538)
    botch=botguild.get_channel(1098236195240165467)
    botmes=await botch.fetch_message(1098236572266151967)
    contents=botmes.content.split("\n")
    
    for content in contents:
        urls= separate_URL(content)
        
        if payload.message_id == int(urls[2]):
            user = client.get_user(payload.user_id)
            stamp = payload.emoji.name
            await message.add_reaction(stamp, user)
    
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

    #
    # rulesのメッセージの👍をクリックしたときの処理
    #
    #

    if payload.message_id == 1092095707164463194:
        user = client.get_user(payload.user_id)
        stamp = payload.emoji.name
        await message.remove_reaction(stamp, user)
        await user.send("ITC BOT 2023です！個人にDMを送信しづらい場合や、誰に質問していいかわからない場合はここに質問をしてください。")


"""
!さいころ
サイコロを回して1~6の乱数を生成

"""


@ client.hybrid_command(description = "サイコロを回して1~6の乱数を生成")
async def さいころ(ctx):

    num = random.randrange(6)
    file = f"img/saikoro/saikoro{num}.gif"
    await ctx.send(file=discord.File(file))

"""
!じゃんけん

"""


@ client.hybrid_command(description = "じゃんけん (グー) (チョキ) (パー)のいずれかを入力")
async def じゃんけん(ctx, arg):
    te = ["gu", "choki", "pa"]
    num = random.randrange(3)
    if arg == "グー":
        file = f"img/janken/gu{te[num]}.gif"
    elif arg == "チョキ":
        file = f"img/janken/choki{te[num]}.gif"
    elif arg == "パー":
        file = f"img/janken/pa{te[num]}.gif"

    await ctx.send(file=discord.File(file))


"""
!kariumi
kariumiに要確認ロールを付与する
後で消す
"""


@ client.command()
async def kariumi(ctx, *arg):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    await ctx.send(arg[0])

"""
!get_now_VC
"""
@client.hybrid_command(description = "現在VCにいる人の一覧を表示")
async def get_now_ch_members(ctx):
    
    members = ctx.channel.members
    message = "現在のVCにいる人一覧：\n"
    for member in members:
        message+=f"・{member.name}\n"
    await ctx.send(message)
#


"""
DMを受け取ったときの処理（TwitterのDMみたいなシステムで相互に返信可）

"""


@ client.listen()
async def on_message(message):
    if message.author == client.user:
        return

    # DMを管理するサーバー
    guild = client.get_guild(1075592226534600755)

    # 本鯖
    itcGuild = client.get_guild(377392053182660609)

    # 新歓鯖
    shinkanGuild = client.get_guild(1056591502958145627)

    # DMカテゴリーの取得
    DMcategory = client.get_channel(1076657448200458362)

    # test送信用のtextchannel
    test_channel = client.get_channel(1075592227180527699)

    # DMを受け取る→データベースに送信　
    if type(message.channel) == discord.DMChannel:
        database = await client.get_channel(1076661281131601940).fetch_message(1076864300200755261)
        data_ = database.content.split("\n")
        for i in data_:
            data = i.split(" ")
            if int(data[0]) == message.author.id:
                sendMes = await client.get_channel(int(data[1])).send(message.content)
                await printLog(client, f"BOTが{message.author.name}からDMを受け取りました。\n{sendMes.jump_url}")
                return
        # 初めて送ってきた人はチャンネルを作成する
        channel = await guild.create_text_channel(message.author.name, category=DMcategory)
        send_Mes = await client.get_channel(channel.id).send(f"【{message.author.name}】\n\n{message.content}")
        new_database = f"{database.content}"
        new_database += f"\n{message.author.id} {channel.id}"
        await database.edit(content=new_database)
        await printLog(client, f"BOTが{message.author.name}からDMを初めて受け取りました。\n{sendMes.jump_url}\nDBに{message.author.name}を追加します。\n{database.jump_url}")
        return
    # データベースに返信を書き込む→DM送信
    if message.channel.category == DMcategory:
        database = await client.get_channel(1076661281131601940).fetch_message(1076864300200755261)
        data_ = database.content.split("\n")
        for i in data_:
            data = i.split(" ")
            if int(data[1]) == message.channel.id:
                try:  # try→本鯖にいるメンバーを取得、except→新歓鯖にいるメンバーを取得、どちらにもいないとバグる
                    member = itcGuild.get_member(int(data[0]))
                    await printLog(client, f"本鯖に、{member.name}がいます")
                except:
                    member = shinkanGuild.get_member(int(data[0]))
                    await printLog(client, f"本鯖には、{member.name}がいませんでした。")
                await member.send(message.content)
                await printLog(client, f"BOTから、{member.name}にDMを返信しました。\n{message.jump_url}")
                return

    # ロール一斉送信

    RoleCategory = client.get_channel(1076860376924307557)
    ShinkanRoleCategory = client.get_channel(1086441780574167071)

    if message.channel.category == ShinkanRoleCategory:
        await printLog(client, message.channel.topic)
        try:
            role = shinkanGuild.get_role(int(message.channel.topic))
            await printLog(client, f"文章を@{role.name}ロール保持者に一斉送信します。")
            members = role.members
            for member in members:
                await member.send(message.content)
                await printLog(client, f"|{member.name}に送信しました。")
        except:
            await printLog(client, "DM一斉送信に失敗しました。")
        return

    if message.channel.category == RoleCategory:
        await printLog(client, message.channel.topic)
        try:
            role = itcGuild.get_role(int(message.channel.topic))
            await printLog(client, f"文章を@{role.name}ロール保持者に一斉送信します。")

            members = role.members
            for member in members:
                await member.send(message.content)
                await printLog(client, f"|{member.name}に送信しました。")
        except:
            await printLog(client, "DM一斉送信に失敗しました。")
        return


"""
on_raw_reaction_remove

- voteコマンド
    - リアクションを外されたらメンバーリストを更新

"""


@ client.event
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
    
    #リアクションロック
    
    botguild=client.get_guild(1098052668431290538)
    botch=botguild.get_channel(1098236195240165467)
    botmes=await botch.fetch_message(1098236572266151967)
    contents=botmes.content.split("\n")
    
    for content in contents:
        urls= separate_URL(content)
        print(urls[2])
        
        if payload.message_id == int(urls[2]):
            user = client.get_user(payload.user_id)
            stamp = payload.emoji.name
            await message.remove_reaction(stamp, user)


"""
!icon
"""


@ client.hybrid_command(description = "（管理者のみ）アイコン情報取得")
async def icon(ctx):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    guild = client.get_guild(377392053182660609)
    members = guild.members
    for member in members:
        try:
            avatar = member.avatar.url
            await ctx.send(avatar)
        except Exception as e:
            await ctx.send(f"{member.name} - {e}")
"""
!ModifyDatabase [add/remove] channnelID messageID (str)
手動でデータベースをいじれるコマンド。危ないので使用前にデータベースのバックアップをとること

add - 最後の行に追加
remove - 文字列が一致する行を削除


これ消す
"""


@ client.hybrid_command(description = "(管理者のみ) BOTの投稿を修正")
async def modify(ctx, channel: typing.Optional[TextChannel],  mes_id, mes):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    try:
        guild = client.get_guild(1075592226534600755)
        message = await channel.fetch_message(int(mes_id))
        await message.edit(content=mes)
        await printLog(client, f"{message.jump_url} - メッセージを更新しました。")
    except Exception as e:
        await printLog(client, f"{failure(e)}")

"""
体験入部生が60日/90日経過したらお知らせする。
（予定では、botが自動で60日経過でDMを送信し、90日でkickする。）
毎日のログはDB鯖のbot-logに送信します。
60日が経過すると@体験入部のロールを外し、@要確認をつける。
要確認が30日が経過すると、代表にDMを送信する。←未実装？
"""


# ループが実行される時間(UTC)
timess = datetime.time(hour=15, minute=0, tzinfo=utc)


@ tasks.loop(seconds=30)  # time=timeに直すことで一日一回実行に戻せます
async def Trial_entry_explulsion():
    # ログを更新するメッセージ
    DBguild = client.get_guild(1075592226534600755)
    DBchannel = DBguild.get_channel(1088489507923443722)
    DBmessage1 = await DBchannel.fetch_message(1088489590681260032)
    DBmessage2_list = [1097308796080099418, 1097309752775675995, 1097309753778122782,
                       1097309763064307712, 1097309763764768878, 1097309909072236645, 1097309909634261052]
    DBmessage3 = await DBchannel.fetch_message(1097310986496647228)

    message1 = ""
    try:

        # 今の時間を取得
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        nowTime = datetime.datetime.now(JST)
        now = nowTime.strftime('%Y/%m/%d %H:%M:%S')
        now_time = datetime.datetime.now(tz=utc)  # 現在時刻を取得(UTC)
        message1 = f"[{now}]\n"

        message1 += f"**BOTの最新データ** \n"

        message1 += f" - {final_update}\n"

        message1 += f" - UTC時間：{now_time.year}/{now_time.month}/{now_time.day} {now_time.hour}:{now_time.minute}:{now_time.second}\n"

        message1 += f"----------------------------------------------------------------------------------------\n"

    except Exception as e:
        message1 = failure(e)
    await DBmessage1.edit(content=message1)  # ログ
    message2 = ""

    # 体験入部メンバーの一覧を表示/60日超えを選別
    guild = client.get_guild(377392053182660609)  # 本鯖
    taiken_role = guild.get_role(851748635023769630)  # @体験入部
    yo_kakunin_role = guild.get_role(833323166440095744)  # @要確認
    # role = guild.get_role(851748635023769630) #@体験入部
    message2 += f"**体験入部の一覧(UTC基準)**\n - __参加日\t\t\t\t\t\t経過日数\t\t\t\t\t\t名前__\n"
    sorted_taiken_members = sorted(
        taiken_role.members, key=lambda x: x.joined_at)  # 参加日順にソート

    # ここから、60日を超えためんばーを選別
    membersOf60days = []
    time_start_date = datetime.datetime(
        year=2023, month=4, day=1, hour=0, minute=0, second=0, tzinfo=utc)
    DBmes_num = 0
    number = 0
    for member in sorted_taiken_members:
        if member.joined_at > time_start_date:
            member_days = now_time - member.joined_at
        else:
            member_days = now_time - time_start_date
        # member_days.secondsを時分秒に直す
        member_hours = int(member_days.seconds/3600)
        tmp = member_days.seconds % 3600
        member_minutes = int(tmp/60)
        member_seconds = tmp % 60
        message2 += f" - {member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day} {member.joined_at.hour}:{member.joined_at.minute}:{member.joined_at.second}\t**{member_days.days}日**{member_hours}時間{member_minutes}分{member_seconds}秒\t{member.mention}\n"

        if member_days.days >= 60:
            membersOf60days.append(member.name)
            try:
                await member.remove_roles(taiken_role)
                await member.add_roles(yo_kakunin_role)
                await printLog(client, f"{member.mention}に要確認ロールを付与しました。")
            except:
                await printLog(client, f"{member.mention}に要確認ロールを付与できませんでした")
        number += 1
        time.sleep(0.2)
        if number > 10:
            DBmessage2 = await DBchannel.fetch_message(DBmessage2_list[DBmes_num])
            await DBmessage2.edit(content=message2)
            message2 = ""
            time.sleep(1)
            number = 0
            DBmes_num += 1
    message2 += f"----------------------------------------------------------------------------------------\n"
    # await DBmessage2.edit(content=message2)  # ログ

    message3 = ""

    message3 += f"**要確認の一覧(UTC基準)**\n - __要確認日\t\t\t\t経過日数\t\t\t\t\t\t名前__\n"
    YoukakuninCH = DBguild.get_channel(1085388068112048241)
    YoukakuninMes = await YoukakuninCH.fetch_message(1087927106509475860)
    mes = YoukakuninMes.content.split("\n")
    for i in mes:
        try:
            data = i.split(" ")

            date = data[1].split("/")
            time__ = data[2].split(":")
            time_ = datetime.datetime(
                year=int(date[0]), month=int(date[1]), day=int(date[2]), hour=int(time__[0]), minute=int(time__[1]), second=int(time__[2]), tzinfo=utc)
            KeikaDays = now_time - time_
            member_hours = int(KeikaDays.seconds/3600)
            tmp = member_days.seconds % 3600
            member_minutes = int(tmp/60)
            member_seconds = tmp % 60
            member_ = guild.get_member(int(data[0]))
            member_name = member_.mention

            message3 += f" - {data[1]} {data[2]}\t**{KeikaDays.days}日**{member_hours}時間{member_minutes}分{member_seconds}秒\t{member_name}\n"
        except:
            message3 += f" - {data[1]} {data[2]}\t**{KeikaDays.days}日**{member_hours}時間{member_minutes}分{member_seconds}秒\t名前不明❓({data[0]})\n"

    await DBmessage3.edit(content=message3)  # ログ


"""
作業部屋入出した時に通知を送信するようにする。



"""


@ client.event
async def on_voice_state_update(member, before, after):
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    nowTime = datetime.datetime.now(JST)
    now = nowTime.strftime('%Y/%m/%d %H:%M:%S')
    sagyoBeya = [833684506790723614, 1092178739451920425, 1096708775525744782,
                 822408934664306699, 822408969342550036, 818756552642527262, 828283228971859978]

    DBguild = client.get_guild(1075592226534600755)
    DBch = DBguild.get_channel(1096722589960917073)
    DBmes = await DBch.fetch_message(1096723359045255238)
    auths = DBmes.content.split("\n")

    try:
        # 作業部屋の通知チャンネル
        ITCguild = client.get_guild(377392053182660609)
        sagyou_TextCh = ITCguild.get_channel(822446386707824700)

        if not before.channel and after.channel:
            await printLog(client, f"name:{member.mention}, 入室VC:{after.channel.name}")

            if after.channel.id in sagyoBeya:

                # for auth in auths:
                #    if member.id == int(auth):
                #        # ここに処理を書く
                # await sagyou_TextCh.send(
                #    f"[{now}] {member.mention}が{after.channel.mention}に入室しました")
                for auth in auths:
                    member_ = ITCguild.get_member(int(auth))
                    await member_.send(
                        f"[{now}] {member.mention}が{after.channel.mention}に入室しました")
    except Exception as e:
        await printLog(client, failure(e))


@ client.hybrid_command(description = "(BOTへのDMのみ) ボイスチャンネル入室通知オン")
async def 通知オン(ctx):

    DBguild = client.get_guild(1075592226534600755)
    DBch = DBguild.get_channel(1096722589960917073)
    DBmes = await DBch.fetch_message(1096723359045255238)

    mes = DBmes.content
    if not (str(ctx.author.id) in mes.split("\n")):
        mes += f"\n{ctx.author.id}"
    await DBmes.edit(content=mes)
    await ctx.send(f"{ctx.author.name}が作業部屋に入ったときの通知をオンにしました。")
    await printLog(client, f"{ctx.author.name}が作業部屋に入ったときの通知をオンにしました。")


@ client.hybrid_command(description = "(BOTへのDMのみ) ボイスチャンネル入室通知オフ")
async def 通知オフ(ctx):

    DBguild = client.get_guild(1075592226534600755)
    DBch = DBguild.get_channel(1096722589960917073)
    DBmes = await DBch.fetch_message(1096723359045255238)

    DBid = DBmes.content.split("\n")

    DBid.remove(f"{ctx.author.id}")
    newmes = ""
    for id in DBid:
        newmes += f"{id}\n"

    await DBmes.edit(content=newmes)
    await ctx.send(f"{ctx.author.name}が作業部屋に入ったときの通知をオフにしました。")
    await printLog(client, f"{ctx.author.name}が作業部屋に入ったときの通知をオフにしました。")


"""
@体験入部のロールが付与された時、その人にBOTから自動でDMを送信する
"""


@ client.event
async def on_member_update(before, after):
    # 本鯖で体験入部ロールが付与されたときの処理
    if before.guild.id == 377392053182660609:
        guild = client.get_guild(377392053182660609)
        role = guild.get_role(851748635023769630)  # 体験入部

        # 送信する文章の取得
        teikeibunCh = client.get_channel(1076714278154932344)
        sendMes = await teikeibunCh.fetch_message(1076714411512840192)

        # roleの差分を取得
        # diff_role = list(set(before.roles) ^ set(after.roles))
        # await printLog(client, f"{before.name}の{diff_role}ロールが変更されました。")
        if (not (role in before.roles)) and (role in after.roles):
            try:
                await before.send(sendMes.content)
                await printLog(client, f"{before.name}に「体験入部が付与された時」のDMを送信しました。")
            except:  # 失敗したら報告
                await printLog(client, f"Error!!：{before.name}に「体験入部が付与された時」のDMを送信できませんでした。")
            return
    # 新歓鯖で体験入部ロールが付与されたときの処理
    if before.guild.id == 1056591502958145627:
        guild = client.get_guild(1056591502958145627)
        role = guild.get_role(1078850225281708122)  # 体験入部

        # 送信する文章の取得
        teikeibunCh = client.get_channel(1076714278154932344)
        sendMes = await teikeibunCh.fetch_message(1086872856551489637)

        # roleの差分を取得
        # diff_role = list(set(before.roles) ^ set(after.roles))
        # await printLog(client, f"{before.name}の{diff_role}ロールが変更されました。")
        if (not (role in before.roles)) and (role in after.roles):
            try:
                await before.send(sendMes.content)
                await printLog(client, f"{before.name}に「新歓鯖で体験入部が付与された時」のDMを送信しました。")
            except:  # 失敗したら報告
                await printLog(client, f"Error!!：{before.name}に「新歓鯖で体験入部が付与された時」のDMを送信できませんでした。")
            return

    # 本鯖で要確認ロールを付与されたときの処理
    if before.guild.id == 377392053182660609:
        guild = client.get_guild(377392053182660609)
        role = guild.get_role(833323166440095744)  # 要確認

        # 要確認の人のデータベース
        youkakuninCh = client.get_channel(1085388068112048241)
        database = await youkakuninCh.fetch_message(1087927106509475860)

        now_time = datetime.datetime.now(tz=utc)  # 現在時刻を取得

        if (not (role in before.roles)) and (role in after.roles):
            new_database = f"{database.content}\n{before.name} {before.id} {now_time.year}/{now_time.month}/{now_time.day} {now_time.hour}:{now_time.minute}:{now_time.second}"
            await database.edit(content=new_database)
            await printLog(client, f"{before.name}に要確認ロールを付与しました")

    # 本鯖で要確認ロールを剥奪されたときの処理
    if before.guild.id == 377392053182660609:
        guild = client.get_guild(377392053182660609)
        role = guild.get_role(833323166440095744)  # 要確認

        # 要確認の人のデータベース
        youkakuninCh = client.get_channel(1085388068112048241)
        database = await youkakuninCh.fetch_message(1087927106509475860)

        now_time = datetime.datetime.now(tz=utc)  # 現在時刻を取得

        if (role in before.roles) and (not (role in after.roles)):
            new_database = f""
            data = database.content.split("\n")

            for i in data:
                data_ = i.split(" ")

                if data_[1] != str(before.id):
                    new_database += f"{i}\n"
                else:
                    await printLog(client, f"{before.name}から要確認ロールを剥奪しました")

            await database.edit(content=new_database)


@client.hybrid_command(description = "（管理者のみ）sendテストコマンド")
async def test(ctx):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    await ctx.send("test1")
    
@client.command()
async def DM_send(ctx):
    authority = authority_check(client, ctx)
    if not authority:
        await ctx.send(embed=authority_error())
        await printLog(client, "!vote_role : Error00")
        return
    guild = client.get_guild(377392053182660609)
    list=[599515603484672002, 832946276127473665, 696712425751445596,761513635221864459, 846690579139919882, 826112080855302195,1093448559061389322, 791628451505242142, 490868059985281024, 733293783600463892, 712874096039559209, 1093062903306915842, 1089209148467597485, 1097834303792091167, 1095677777983836180, 1095635437642596352,  1093560701437612202, 1093412359135043664, 997868516654972958,  876676335911727125,  853550282918068224, 613523406671052831, 347663185328996354,723702538154803310, 505293333434990602, 1093145200311930910, 637497539930882053, 1093496054776868916, 1093894948039962644 ]
    for member_id in list:
        member = guild.get_member(member_id)
        str_ = f"4/20の対面部会の抽選の結果ですが、{member.name}は**__当選__**しました！！是非ご参加下さい！！\n\n●開催日時：4/20(木)　18:00~20:00まで予約済み\n●開催場所：407教室"
        
        await member.send(str_)

"""
権限の確認
"""
token = getenv('DISCORD_BOT_TOKEN')
client.run(token)
