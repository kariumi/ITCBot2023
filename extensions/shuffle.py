from discord.ext import commands
from discord import Role, VoiceChannel
import typing

import random

from .utils.bot_error import *
from .utils.others import *

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


class Shuffle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def shuffle(self, ctx, host1: typing.Optional[Role] = None, host2: typing.Optional[Role] = None, host3: typing.Optional[Role] = None, *channels: VoiceChannel):
        authority = authority_check2(self.bot, ctx)
        if not authority:
            await ctx.send(embed=authority_error())
            await printLog(self.bot, "!shuffle : Error00")
            return
        if ctx.author.voice is None:
            await ctx.send(embed=any_error("ボイスチャンネルに入ってください", ""))
            printLog(self.bot, "!shuffle : Error01")
            return
        if len(channels) == 0:
            await ctx.send(embed=any_error("ボイスチャンネルを指定してください", ""))
            printLog(self.bot, "!shuffle : Error02")
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

        await printLog(self.bot, f"{channel.mention}に接続している人を移動させました")


async def setup(bot):
    await bot.add_cog(Shuffle(bot))
