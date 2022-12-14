import os
import discord
from discord.ext import commands
from module.json_module import open_json
from server import keep_alive

#botの設定ファイルを開く
settings = open_json('settings/appsettings.json')

#botの情報を取得
prefix = settings['prefix']
token = os.getenv('DISCORD_BOT_TOKEN')

#インテント有効化
intents = discord.Intents.all()

#botを作成
bot = commands.Bot(intents=intents, command_prefix=prefix)

bot.load_extension('event_listener')
bot.load_extension('feature')

#ウェブサーバー->botを起動
try:
    keep_alive()
    bot.run(token)
except Exception as e:
    print(e)
    os.system("kill 1")