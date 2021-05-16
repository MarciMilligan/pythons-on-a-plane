import os
import discord
from discord.ext import commands

TOKEN = ""  # discord webhook token
client = discord.Client()
bot = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


bot = commands.Bot(command_prefix='!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return


    if message.content.startswith('!export'):
       channel = client.get_channel(817962513433493517)
       os.system('python3 driver.py')
       await channel.send(file=discord.File('planesPlot.png'))


    if message.content.startswith('!help'):
        msg1 = 'Use !export to print airplanes over you!'.format(message)
        await message.channel.send(msg1)


client.run(TOKEN)
