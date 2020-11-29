# Among Us scorekeeping bot
# Trevor Day

import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

STATUS = 'BETA' #use BETA tag when testing
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = '.'

# if STATUS == 'BETA':
#     TOKEN = os.getenv('BETA_TOKEN')
#     PREFIX = os.getenv('BETA_PREFIX')
# else:
#     TOKEN = os.getenv('DISCORD_TOKEN')
#     PREFIX = os.getenv('PREFIX')

initial_extensions = [
    "cogs.AUcog"
]

bot = commands.Bot(command_prefix=f'{PREFIX}')

#load cogs
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(f"{'.'}help"))
    print(f'Successfully logged in and booted...!')

bot.run(TOKEN, bot=True)