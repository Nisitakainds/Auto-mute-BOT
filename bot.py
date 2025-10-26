import discord
from discord.ext import commands, tasks
from datetime import datetime, time
import pytz
import os
import threading
from flask import Flask
import requests
import time as t

# -----------------------
# 設定
# -----------------------
GUILD_ID = 1422530481521426484
MOD_LOG_CHANNEL_ID = 1422963315746930782
MUTE_START = time(0, 30)  # 0:30
MUTE_END = time(6, 0)    # 6:00
PING_INTERVAL = 300       # 5分ごとにPing

# 日本時間
JST = pytz.timezone("Asia/Tokyo")

# -----------------------
# Bot 初期化
# -----------------------
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.message_content = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------
# ミュート時間判定
# -----------------------
def is_mute_time():
    now = datetime.now(JST).time()
    if MUTE_START <= MUTE_END:
        return MUTE_START <= now < MUTE_END
    else:
        return now >= MUTE_START or now < MUTE_END

# -----------------------
# Discordへログ送信
# -----------------------
async def send_log(message):
    guild = bot.get_guild(GUILD_ID)
    if guild:
        channel = guild.get_channel(MOD_LOG_CHANNEL_ID)
        if channel:
            try:
                await channel.send(message)
            except:
                pass

# -----------------------
# VCメンバー自動ミュート（管理者除外）
# -----------------------
@tasks.loop(seconds=60)
async def mute_task():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    mute_now = is_mute_time()
    for vc in guild.voice_channels:
        for member in vc.members:
            if member.guild_permissions.administrator:
                continue
            try:
                await member.edit(mute=mute_now)
            except Exception as e:
                await send_log(f"⚠️ ミュート操作エラー: {member.display_name} - {e}")

# -----------------------
# 途中参加者の即ミュート（管理者除外）
# -----------------------
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None and is_mute_time():
        if member.guild_permissions.administrator:
            return
        try:
            await member.edit(mute=True)
            await send_log(f"✅ {member.display_name} を途中参加でサーバーミュート")
        except Exception as e:
            await send_log(f"⚠️ 途中参加ミュートエラー: {member.display_name} - {e}")

# -----------------------
# Bot起動時
# -----------------------
@bot.event
async def on_ready():
    await send_log(f"🟢 Botログイン完了: {bot.user}")
    mute_task.start()

# -----------------------
# スリープ防止 Webサーバー + Ping
# -----------------------
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_server():
    app.run(host="0.0.0.0", port=8080)

def ping_self():
    url = os.environ.get("RAILWAY_STATIC_URL", "http://localhost:8080/")
    while True:
        try:
            requests.get(url, timeout=5)
        except:
            pass
        t.sleep(PING_INTERVAL)

threading.Thread(target=run_server, daemon=True).start()
threading.Thread(target=ping_self, daemon=True).start()

# -----------------------
# Bot起動
# -----------------------
bot.run(os.environ["BOT_TOKEN"])



