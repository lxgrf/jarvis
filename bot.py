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
    user = message.author.name
    command = message.content.split(" ")
    action = command[0]

    if action == "Morning.":
        await message.channel.send("Good morning, {}.".format(user))

    elif action == ".register" or action == ".r":
        if len(command) > 1:
            response = jarvis.register(user, " ".join(command[1:]))
#            await message.author.change_nickname(" ".join(command[1:]))
        else: response = "Who did you wish to register?"
        await message.channel.send(response)

    elif action == ".draw" or action == ".d":
        if len(command) > 1:
            response = jarvis.draw(user, int(command[1]))
        else: response = jarvis.draw(user)
        await message.channel.send(response)
        await message.author.send(jarvis.showhand(user))

    elif action == ".play" or action == ".p":
        if len(command)>1:
            response = jarvis.play(user, int(command[1]))
            await message.author.send(jarvis.showhand(user))
        else: response = "Which card did you wish to play?"
        await message.channel.send(response)

    elif action == ".show" or action == ".s":
        if len(command)>1:
            response = jarvis.show(user, int(command[1]))
        else: response = "Which card did you wish to show?"
        await message.channel.send(response)

    elif action == ".flip" or action == ".f": await message.channel.send(jarvis.flip())

    elif action == ".narrative" or action == ".n":
        pinned = await message.channel.pins()
        for msg in pinned: await msg.unpin()
        pinmsg = await message.channel.send("### Narrative Card\n{}".format(jarvis.flip(narrative = True)))
        await pinmsg.pin()

    elif action == ".peek": await message.channel.send(jarvis.handsizes())

    elif action == '.debug': await message.channel.send(jarvis.debug())

    elif action == '.gameover':
        await message.channel.send("Game over, man, game over!\nAll characters unassigned, all cards returned, deck shuffled.")
        jarvis.reset()
        pinned = await message.channel.pins()
        for msg in pinned: await msg.unpin()

client.run(TOKEN)
