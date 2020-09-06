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
    if message.author == client.user: # Stop the bot from replying to itself
        return
    user = message.author.name
    command = message.content.split(" ")
    action = command[0] # Extract first word to check against commands

    if action == "Morning.":
        await message.channel.send("Good morning, {}.".format(user))

    elif action == ".register" or action == ".r":
        if len(command) > 1: response = jarvis.register(user, " ".join(command[1:]))
#                await message.author.change_nickname(" ".join(command[1:]))
        else: response = "Who did you wish to register?"
        await message.channel.send(response)

    elif action == ".deregister": await message.channel.send(jarvis.deregister(user))

    elif action == ".draw" or action == ".d":
        if len(command) > 1:
            response = jarvis.draw(user, int(command[1]))
        else: response = jarvis.draw(user)
        await message.channel.send(response)
        await message.author.send(jarvis.showhand(user))

    elif action == ".play" or action == ".p":
        if len(command)>1:
            response, doom = jarvis.play(user, int(command[1]))
                 # play returns two messages, the second being the string for moving Doom to the GM's hand. Blank if that didn't happen.
                 # Splitting it up cleaned up the formatting, as it shows embedded images at the end of the message rather than inline
            await message.author.send(jarvis.showhand(user))
        else: response = "Which card did you wish to play?"
        await message.channel.send(response)
        if doom is not "": await message.channel.send(doom)

    elif action == ".show" or action == ".s":
        if len(command)>1: response = jarvis.show(user, int(command[1]))
        else: response = "Which card did you wish to show?"
        await message.channel.send(response)

    elif action == ".flip" or action == ".f": 
        await message.channel.send("Random card from deck\n{}".format(jarvis.flip()))

    elif action == ".narrative" or action == ".n":
        pinned = await message.channel.pins() # Get all pinned message IDs
        for msg in pinned: await msg.unpin() # Then get rid of them
        pinmsg = await message.channel.send("### Narrative Card\n{}".format(jarvis.flip(narrative = True)))
        await pinmsg.pin()

    elif action == ".boost" or action == ".brain" or action == ".b":
        if len(command)>1: response = jarvis.boost(user, command[1])
        else: response = jarvis.boost(user)
        await message.channel.send(response)

    elif action == ".peek": await message.channel.send(jarvis.handsizes())

    elif action == ".gm": await message.channel.send("GM's hand:\n{}".format(jarvis.showhand()))

    elif action == '.debug': await message.channel.send(jarvis.debug())
              #Lists everyone's cards. For debug purposes only. Disable before real games if you like.

    elif action == '.gameover':
        await message.channel.send("Game over, man, game over!\nAll characters unassigned, all cards returned, deck shuffled.")
        jarvis.reset()
        pinned = await message.channel.pins()
        for msg in pinned: await msg.unpin()

    elif action == '.test': await message.author.send_file(handimage(user))

client.run(TOKEN)
