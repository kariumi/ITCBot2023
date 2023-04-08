import discord

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