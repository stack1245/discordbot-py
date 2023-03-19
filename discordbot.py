from cmath import log
from distutils.sysconfig import PREFIX
import discord
from dotenv import load_dotenv
import os
load_dotenv()

PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']

bot = discord.Client()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == f'{PREFIX}call':
        await message.channel.send("callback!")

    if message.content.startswith(f'{PREFIX}hello'):
        await message.channel.send('Hello!')

@bot.event
async def on_message(message):
    if message.content == "!":
        await message.channel.send("명령어를 입력해주세요.")
    await bot.process_commands(message)


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="**🔐 RBT 도움말**", description="by 스택#1107 from NitrogenBot", color=0x56792b)
    embed.add_field(
        name="**!admin add [id]**", value="`디스코드 봇 관리자 권한을 부여합니다.`", inline=False)
    embed.add_field(
        name="**!admin remove [id]**", value="`디스코드 봇 관리자 권한을 박탈합니다.`", inline=False)
    embed.add_field(name="**!admin list**",
                    value="`디스코드 봇 관리자 권한을 가진 유저를 모두 표시합니다.`", inline=False)
    embed.add_field(name="**!경고 [player] [value]**",
                    value="`플레이어에게 [value]만큼 경고를 추가합니다.`", inline=False)
    embed.add_field(name="**!경고차감 [player] [value]**",
                    value="`플레이어에게 [value]만큼 경고를 제거합니다.`", inline=False)
    embed.add_field(name="**!경고목록**",
                    value="`경고를 가진 유저를 모두 표시합니다.`", inline=False)
    embed.add_field(name="**!방이름 [id]**",
                    value="`방 아이디의 방 이름을 표시합니다.`", inline=False)
    await ctx.reply(embed=embed)


@bot.command()
async def 방이름(ctx, channel_id: str):
    if not channel_id.isnumeric():
        await ctx.reply("> 사용방법\n`!방이름 [id]`")
        return

    channel = bot.get_channel(int(channel_id))
    if channel is None:
        await ctx.reply("해당하는 채널을 찾을 수 없습니다.")
        return

    await ctx.reply(f"> **{channel_id}**번 채널의 이름\n**{channel.name}**")


@bot.command()
async def admin(ctx, option: str, user: discord.Member = None):
    if ctx.author.id not in admins:
        return await ctx.reply("어드민만 사용 가능한 명령어입니다.")

    if option == "add":
        if user:
            if user.id in admins:
                return await ctx.reply("해당 유저는 이미 어드민입니다.")
            admins.append(user.id)
            await ctx.reply(f"{user.name}({user.id})이(가) 어드민으로 추가되었습니다.")
        else:
            return await ctx.reply("> 사용방법\n`!admin add [id]`")

    elif option == "remove":
        if user:
            if user.id not in admins:
                return await ctx.reply("해당 유저는 어드민이 아닙니다.")
            admins.remove(user.id)
            await ctx.reply(f"{user.name}({user.id})이(가) 어드민에서 제거되었습니다.")
        else:
            return await ctx.reply("> 사용방법\n`!admin remove [id]`")

    elif option == "list":
        embed = discord.Embed(
            title="어드민 목록", description="by 스택#1107", color=0x00ff00)
        admin_list = [f"{(await bot.fetch_user(admin_id)).name}({admin_id})" for admin_id in admins]
        embed.add_field(name="**어드민 목록**",
                        value="\n".join(admin_list), inline=False)
        await ctx.reply(embed=embed)

    else:
        await ctx.reply("올바른 명령어 옵션을 입력해주세요.")


warning_channel_ids = [1078995386045300768, 1087019687503740958]
warnings = {}
ban_words = ['씨발', 'ㅆㅂ', '시발', 'ㅅㅂ', '욕123']


@bot.event
async def on_message(message):
    if message.channel.id in warning_channel_ids and any(word in message.content for word in ban_words):
        author_id = message.author.id
        if author_id not in warnings:
            warnings[author_id] = 0
        warnings[author_id] += 1
        await message.reply(f"{message.author.name}님 욕은 나빠요!\n경고 +1")
    await bot.process_commands(message)


@bot.command()
async def 경고차감(ctx, member: discord.Member = None, value: int = 1):
    if ctx.author.id not in admins:
        return await ctx.reply("어드민만 사용 가능한 명령어입니다.")
    if not member or not value:
        return await ctx.reply("> 사용방법\n`!경고차감 [player] [value]`")

    if member.id not in warnings:
        return await ctx.reply("해당 플레이어는 경고를 받은 적이 없습니다.")

    if warnings[member.id] < value:
        value = warnings[member.id]

    warnings[member.id] -= value
    await ctx.reply(f"{member.name}님의 경고가 {value}개 제거되었습니다.\n현재 경고 횟수 : {warnings[member.id]}")


@bot.command()
async def 경고목록(ctx):
    embed = discord.Embed(
        title="경고 목록", description="경고를 받은 유저와 횟수입니다.", color=0xFF0000)
    has_warnings = False
    for user_id, count in warnings.items():
        if count > 0:
            has_warnings = True
            user = await bot.fetch_user(user_id)
            embed.add_field(name=user.display_name,
                            value=f"{count}회 경고", inline=False)
    if not has_warnings:
        embed.add_field(name="현재 경고를 받은 사람은 없습니다.", value="\u200b")
    await ctx.reply(embed=embed)


try:
    client.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")
