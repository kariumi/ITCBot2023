import random

import typing

import emoji
import sqlite3
from discord import TextChannel, VoiceChannel, Role, Intents
from discord.ext import commands

import settings

intents = Intents.default()
intents.members = True
client = commands.Bot(command_prefix=("!", "！"), intents=intents)

DATABASE_URL = settings.dbname


@client.command()
async def vote(ctx, text: str, *choices):
    if len(choices) == 0:
        await ctx.send("選択肢を指定してください")
        return

    if len(choices) % 2 != 0:
        await ctx.send("選択肢は選択肢と絵文字をセットで指定してください\n"
                       "例:りんご 🍎 みかん 🍊 ぶどう 🍇")
        return

    s = ""
    emojis = []
    for i in range(int(len(choices) / 2)):
        if not choices[i * 2 + 1] in emoji.EMOJI_DATA:
            await ctx.send("選択肢は選択肢と絵文字をセットで指定してください\n"
                           "例:りんご 🍎 みかん 🍊 ぶどう 🍇\n"
                           "なお、カスタム絵文字は使えません")
            return

        s += f"{choices[i * 2]} {choices[i * 2 + 1]}\n{''.join([':white_large_square:' for i in range(20)])} (0票)\n"
        emojis.append(choices[i * 2 + 1])

    message = await ctx.send(f"{ctx.author.display_name}さんが投票を開始しました\n"
                             f"投票内容: {text}\n\n"
                             f"選択肢\n{s}")

    for e in emojis:
        await message.add_reaction(e)

    send_data(f"INSERT INTO votes (message_id, channel_id, emojis) VALUES (\'{message.id}\', \'{ctx.channel.id}\', \'{''.join(emojis)}\')")


@client.command()
async def vote_history(ctx, channel: typing.Optional[TextChannel] = None, num: typing.Optional[int] = 10):
    urls = []
    if channel is None:
        channel = ctx.channel
    for d in get_data(f"SELECT channel_id, message_id FROM votes WHERE channel_id = \'{channel.id}\' ORDER BY id DESC LIMIT {num}"):
        message = await client.get_channel(int(d[0])).fetch_message(int(d[1]))
        urls.append(message.jump_url)
    await ctx.send(f"{channel.mention} には投票がありません" if len(urls) == 0 else "\n".join(urls))


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.ChannelNotFound):
        await ctx.send("指定したチャンネルが見つかりません")
    elif isinstance(error, commands.CommandNotFound):
        return
    raise error


@client.command()
async def shuffle(ctx,
                  host1: typing.Optional[Role] = None,
                  host2: typing.Optional[Role] = None,
                  host3: typing.Optional[Role] = None,
                  host4: typing.Optional[Role] = None,
                  *channels: VoiceChannel):
    if not ctx.guild.get_role(968160313797136414) in ctx.author.roles:
        await ctx.send("実行権限がありません")
        return
    if ctx.author.voice is None:
        await ctx.send("ボイスチャンネルに入ってください")
        return
    if len(channels) == 0:
        await ctx.send("ボイスチャンネルを指定してください")
        return
    channel = ctx.author.voice.channel

    members = channel.members
    hosts = []

    for m in members[:]:
        if host1 is not None and host1 in m.roles:
            hosts.append(m)
            members.remove(m)
            continue

        if host2 is not None and host2 in m.roles:
            hosts.append(m)
            members.remove(m)
            continue

        if host3 is not None and host3 in m.roles:
            hosts.append(m)
            members.remove(m)
            continue

        if host4 is not None and host4 in m.roles:
            hosts.append(m)
            members.remove(m)
            continue

    random.shuffle(members)
    random.shuffle(hosts)

    for i in range(len(members)):
        await members[i].move_to(channels[i % len(channels)])
    for i in range(len(hosts)):
        await hosts[i].move_to(channels[i % len(channels)])

    await ctx.send(f"{channel.mention}に接続している人を移動させました")


@client.event
async def on_ready():
    print(f"{client.user}でログインしました")


@client.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return
    if payload.emoji.name not in emoji.EMOJI_DATA:
        return

    if len(get_data(f"SELECT * FROM votes WHERE message_id = \'{payload.message_id}\'")) != 1:
        return

    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    content = message.content.split("\n")
    reactions = message.reactions
    emoji_ = payload.emoji.name
    user_id = payload.user_id
    emojis = get_data(f"SELECT emojis FROM votes WHERE message_id = {payload.message_id}")[0][0]

    for r in reactions[:]:
        if not r.emoji in emojis:
            reactions.remove(r)

    if emoji_ in emojis:
        for r in reactions:
            async for user in r.users():
                if emoji_ != r.emoji and user.id == user_id:
                    await r.remove(user)

    await update_vote(message, content, reactions)


@client.event
async def on_raw_reaction_remove(payload):
    user = await client.fetch_user(payload.user_id)
    if user.bot:
        return

    if len(get_data(f"SELECT * FROM votes WHERE message_id = \'{payload.message_id}\'")) != 1:
        return

    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    content = message.content.split("\n")
    reactions = message.reactions
    emojis = get_data(f"SELECT emojis FROM votes WHERE message_id = {payload.message_id}")[0][0]

    for r in reactions[:]:
        if not r.emoji in emojis:
            reactions.remove(r)

    await update_vote(message, content, reactions)


async def update_vote(message, content, reactions):
    sum_ = 0
    rate = []

    for r in reactions:
        sum_ += r.count - 1

    for r in reactions:
        if sum_ != 0:
            rate.append((r.count - 1) / sum_)

    for i in range(len(reactions)):
        if sum_ == 0:
            content[len(content) - (len(reactions) - i - 1) * 2 - 1] = f"{''.join([':white_large_square:' for i in range(20)])} (0票)"
        else:
            content[len(content) - (len(reactions) - i - 1) * 2 - 1] = ""
            for k in range(20):
                content[len(content) - (len(reactions) - i - 1) * 2 - 1] += ":green_square:" if k < rate[i] * 20 else ":white_large_square:"
            content[len(content) - (len(reactions) - i - 1) * 2 - 1] += f" ({reactions[i].count - 1}票)"

    await message.edit(content=str("\n".join(content)), suppress=False)


def send_data(query):
    conn = sqlite3.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    conn.close()


def get_data(query) -> list:
    conn = sqlite3.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()

    return result


client.run(settings.TOKEN)
