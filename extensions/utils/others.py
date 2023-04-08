import datetime

utc = datetime.timezone.utc

"""
ログを残す
printLog(client, "内容")
"""
async def printLog(bot, content):
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    nowTime = datetime.datetime.now(JST)
    textch = bot.get_channel(1076682589185790065)
    now = nowTime.strftime('%Y/%m/%d %H:%M:%S')
    await textch.send(f"[{now}] - {content}")

"""
権限の確認
"""

def authority_check(client, ctx):
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