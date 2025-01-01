import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# 모든 Intent 활성화
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

user_times = {}  # 유저 입장 시간 저장
daily_usage = {}  # 유저별 총 이용 시간 저장

# 텍스트 채널 ID 설정
TEXT_CHANNEL_ID = 1323488987058540584  # 여기에 '111time' 채널 ID를 입력하세요

# 이미지 URL 설정
ENTER_IMAGE_URL = "https://i.pinimg.com/736x/e7/34/75/e73475fc7610c1ea695efe417cef78d4.jpg"  # 입장용 이미지
EXIT_IMAGE_URL = "https://i.pinimg.com/736x/3b/ce/e3/3bcee3ef83f32a13552fb20f3476a9e7.jpg"  # 퇴장용 이미지

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not send_daily_summary.is_running():
        send_daily_summary.start()  # 하루 집계 메시지 보내는 태스크 시작

@bot.event
async def on_voice_state_update(member, before, after):
    global user_times, daily_usage

    # 텍스트 채널 객체 가져오기
    text_channel = bot.get_channel(TEXT_CHANNEL_ID)

    # 유저가 음성 채널에 들어올 때
    if before.channel is None and after.channel is not None:
        user_times[member.id] = datetime.now()

        # 텍스트 채널에 메시지 전송
        if text_channel:
            embed = discord.Embed(
                title="⭐ 새로운 별이 탄생하는 순간 ⭐",
                description=(
                    f"{member.mention} 님 어서오세요!\n"
                    f"**BIG BANG:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                ),
                color=discord.Color.green()
            )
            embed.set_image(url=ENTER_IMAGE_URL)
            embed.set_footer(text="별지기와 함께하는 즐거운 시간")
            await text_channel.send(embed=embed)

    # 유저가 음성 채널에서 나갈 때
    elif before.channel is not None and after.channel is None:
        start_time = user_times.pop(member.id, None)
        if start_time:
            duration = datetime.now() - start_time

            # 총 이용 시간 업데이트
            if member.id in daily_usage:
                daily_usage[member.id] += duration
            else:
                daily_usage[member.id] = duration

            # 텍스트 채널에 메시지 전송
            if text_channel:
                embed = discord.Embed(
                    title="✨ 오늘 당신의 시간이 예쁜 별을 만들었어요 ☺",
                    description=(
                        f"**사용시간:** {str(duration).split('.')[0]}"
                    ),
                    color=discord.Color.red()
                )
                embed.set_image(url=EXIT_IMAGE_URL)
                embed.set_footer(text="별지기와 함께하는 추억 저장 중...")
                await text_channel.send(embed=embed)

@tasks.loop(minutes=1)
async def send_daily_summary():
    # 매일 자정에 집계 메시지를 보냄
    now = datetime.now()
    target_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    sleep_time = (target_time - now).total_seconds()
    if sleep_time > 0:
        await asyncio.sleep(sleep_time)

    text_channel = bot.get_channel(TEXT_CHANNEL_ID)
    if text_channel:
        embed = discord.Embed(
            title="🌟 하루 이용 시간 요약 🌟",
            description="모든 사용자의 음성 채널 총 이용 시간이 집계되었습니다.",
            color=discord.Color.blue()
        )
        for user_id, total_time in daily_usage.items():
            user = await bot.fetch_user(user_id)
            embed.add_field(
                name=user.name,
                value=f"총 이용 시간: {str(total_time).split('.')[0]}",
                inline=False
            )
        embed.set_footer(text="별지기와 함께하는 하루 마무리")
        await text_channel.send(embed=embed)

        # 집계 초기화
        daily_usage.clear()

# 봇 실행
bot.run(BOT_TOKEN)
