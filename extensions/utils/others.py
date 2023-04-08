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