import datetime


utc = datetime.timezone.utc


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


"""
ログを残す
printLog(client, "内容")
"""


async def printLog(bot, content):
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    nowTime = datetime.datetime.now(JST)
    now = nowTime.strftime('%Y/%m/%d %H:%M:%S')
    textch = bot.get_channel(1076682589185790065)
    await textch.send(f"[{now}] - {content}")

"""
権限の確認
"""

# BOT使用の人のみ使えます。
#
#


def authority_check(client, ctx):
    # コマンドを使用した鯖でこのロールが付与されていたら使用できる。BOT使用
    true_role = [968160313797136414]
    # true_guildの鯖ではロールなしでも使える。DB鯖/TEST鯖
    true_guild = [1075592226534600755, 1053669243616501800]

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


# こっちの方はBOT使用(一時)の人も使えます
#
#
def authority_check2(client, ctx):
    # コマンドを使用した鯖でこのロールが付与されていたら使用できる。BOT使用/BOT使用(一時)
    true_role = [968160313797136414, 1096674116473462865]
    # true_guildはtrue_roleと一対一対応で。
    true_guild = [1075592226534600755, 1053669243616501800]

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


def get_startup_jst():
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    nowTime = datetime.datetime.now(JST)
    now = nowTime.strftime('%Y/%m/%d %H:%M:%S')
    final_update = "BOT更新日：" + now
    return final_update
