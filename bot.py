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
GUILD_ID = 123456789012345678  # ★自分のサーバーIDに置き換えてください
MUTE_START = time(0, 0)  # ミュート開始 0:00
MUTE_END = time(6, 0)    # ミュート解除 6:00
PING_INTERVAL = 300       # 自分自身を5分ごとにPing

# 日本時間
JST = pytz.timezone("Asia/Tokyo")

# -----------------------
# Bot 初期化
# -----------------------
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------
# ミュート時間判定
# -----------------------
def is_mute_time():
    now = datetime.now(JST).time()
    return MUTE_START <= now < MUTE_END

# -----------------------
# 定期タスク：一斉ミュート/解除
# -----------------------
@tasks.loop(seconds=60)
async def mute_task():
    now = datetime.now(JST).time()
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    if now.hour == MUTE_START.hour and now.minute == MUTE_START.minute:
        for vc in guild.voice_channels:
            for member in vc.members:
                await member.edit(mute=True)
        print("0:00 全員サーバーミュートしました")

    if now.hour == MUTE_END.hour and now.minute == MUTE_END.minute:
        for vc in guild.voice_channels:
            for member in vc.members:
                await member.edit(mute=False)
        print("6:00 全員サーバーミュート解除しました")

# -----------------------
# 途中参加者の即ミュート
# -----------------------
@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        if is_mute_time():
            await member.edit(mute=True)
            print(f"{member.display_name} を途中参加でサーバーミュートしました")

# -----------------------
# Bot起動時
# -----------------------
@bot.event
async def on_ready():
    print(f"ログイン完了: {bot.user}")
    mute_task.start()

# -----------------------
# 簡易Webサーバー（スリープ対策用）
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
            requests.get(url)
        except:
            pass
        t.sleep(PING_INTERVAL)

# スレッドで並行実行
threading.Thread(target=run_server).start()
threading.Thread(target=ping_self).start()

# -----------------------
# Bot起動
# -----------------------
bot.run(os.environ["BOT_TOKEN"])

import os
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

# Bot起動時に環境変数からトークンを取得
bot.run(os.environ["BOT_TOKEN"])

import os
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

# Bot起動時に環境変数からトークンを取得
bot.run(os.environ["RAILWAY_STATIC_URL"])

