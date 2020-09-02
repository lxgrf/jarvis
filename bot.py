# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 19:49:03 2020

@author: apgri
"""

import os

import discord
from dotenv import load_dotenv
import jarvis

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    command = message.content.split(" ")
    action = command[0]
    if action == "Morning.":
        await message.channel.send("Good morning, sir.")
    elif action == ".register" or action == ".r":
        if len(command) > 1: 
            response = jarvis.register(command[1])
            await message.channel.send(response)
    

client.run(TOKEN)