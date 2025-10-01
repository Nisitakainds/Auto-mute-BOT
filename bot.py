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
MUTE_START = time(0, 0)       # ミュート開始 0:00
MUTE_END = time(6, 0)         # ミュート解除 6:00
PING_INTERVAL = 300            # 5分ごとにPing

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
# VCメンバー自動ミュート
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
                continue  # 管理者はスキップ
            try:
                await member.edit(mute=mute_now)
            except:
                pass

# -----------------------
# 途中参加者の即ミュート
# -----------------------
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None and is_mute_time():
        if member.guild_permissions.administrator:
            return
        try:
            await member.edit(mute=True)
        except:
            pass

# -----------------------
# Bot起動時
# -----------------------
@bot.event
async def on_ready():
    print(f"ログイン完了: {bot.user}")
    mute_task.start()

# -----------------------
# スリープ対策 Webサーバー + Ping
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
