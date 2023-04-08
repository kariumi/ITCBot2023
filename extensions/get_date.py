from discord.ext import commands
from discord import Role
import typing

from .utils.bot_error import *
from .utils.others import *

"""
!get_date [ロール]
指定ロールに所属しているメンバーのサーバー参加日/その日からの経過日数を教えてくれる。
体験入部の管理用に作ったけどそっちは自動でやってくれるので手動で実行することはほぼない。

!get_date_id [ロール]
指定ロールに所属しているメンバーのサーバー参加日/その日からの経過日数を教えてくれる。
体験入部の管理用に作ったけどそっちは自動でやってくれるので手動で実行することはほぼない。

"""

class GetDate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_date(self, ctx, role: typing.Optional[Role] = None):

        if role == None:
            await ctx.send(embed=get_date_error("ロールが指定されていません！"))
            await printLog(self.bot, "!get_date : Error01")
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

    @commands.command()
    async def get_date_id(self, ctx, role_id):
        guild = self.bot.get_guild(377392053182660609)
        role = guild.get_role(int(role_id))

        if role == None:
            await ctx.send(embed=get_date_error("ロールが指定されていません！"))
            await printLog(self.bot, "!get_date : Error01")
            return

        now_time = datetime.datetime.now(tz=utc)  # 現在時刻を取得

        message = f"__{role.name}の一覧:{now_time.year}/{now_time.month}/{now_time.day} {now_time.hour}:{now_time.minute}\n__\n__参加日\t\t経過日数\t名前__\n"

        sorted_taiken_members = sorted(
            role.members, key=lambda x: x.joined_at)  # 参加日順にソート

        for member in sorted_taiken_members:
            # ログ用
            member_days = now_time - member.joined_at
            message += f"{member.joined_at.year}/{member.joined_at.month}/{member.joined_at.day}\t{member_days.days}日\t{member.name}\n"

        await ctx.send(message)  # ログ

async def setup(bot):
    await bot.add_cog(GetDate(bot))