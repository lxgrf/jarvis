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
valid_channels = ["general", "test"]

async def hand(message, user):
    imagefile, GM, zaps = jarvis.handimage(user)
    if imagefile:
        if GM: 
            title = "GM's Hand"
            description = ""
        else: 
            title = "Your Hand"
            description = "Card index numbers are in the bottom left of each card."
            if len(zaps)>0: description += "\nTokens: {}".format(zaps)
        embed = discord.Embed(title=title, description=description, color=0x0ff00)
        file = discord.File(imagefile, filename = "image.jpg")
        embed.set_image(url="attachment://image.jpg")
        if GM: await message.channel.send(file=file, embed=embed)
        else: await message.author.send(file=file, embed=embed)
    else: await message.channel.send("There are no cards in that hand.")

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

    if str(message.channel) not in valid_channels: action = ".invalid"

    if action == "Morning.": await message.channel.send("Good morning, {}.".format(user))

    if action == ".invalid": await message.channel.send("Alas, I am not permitted to act on commands in this channel.")

    elif action == ".register" or action == ".r":
        if len(command) > 1: response = jarvis.register(user, " ".join(command[1:]))
        else: response = "Who did you wish to register?"
        await message.channel.send(response)

    elif action == ".deregister": await message.channel.send(jarvis.deregister(user))

    elif action == ".draw" or action == ".d":
        if len(command) > 1: response = jarvis.draw(user, int(command[1]))
        else: response = jarvis.draw(user)
        await message.channel.send(response)
        await hand(message, user)

    elif action == ".play" or action == ".p":
        if len(command)>1:
            response, doom = jarvis.play(user, int(command[1]))
        else: response = "Which card did you wish to play?"
        await message.channel.send(response)
        await hand(message, user)
        if doom: 
            await message.channel.send("A doom card has been played!")
            await hand(message, user="GM")

    elif action == ".show" or action == ".s":
        if len(command)>1: response = jarvis.show(user, int(command[1]))
        else: response = "Which card did you wish to show?"
        await message.channel.send(response)

    elif action == ".flip" or action == ".f": 
        await message.channel.send("Random card from deck\n{}".format(jarvis.flip(user)[0]))

    elif action == ".narrative" or action == ".n":
        pinned = await message.channel.pins() # Get all pinned message IDs
        for msg in pinned: await msg.unpin() # Then get rid of them
        x, y = jarvis.flip(user, narrative = True)
        if y:
            pinned = await message.channel.pins()
            for msg in pinned: await msg.unpin()
            pinmsg = await message.channel.send("### Narrative Card\n{}".format(x))
            await pinmsg.pin()
        else: await message.channel.send("Only the GM may draw a Narrative card.")

    elif action == ".boost" or action == ".brain" or action == ".b":
        if len(command)>1: response = jarvis.boost(user, " ".join(command[1:]))
        else: response = jarvis.boost(user)
        await message.channel.send(response)

    elif action == ".peek": await message.channel.send(jarvis.handsizes())

    elif action == ".gm": await hand(message, user="GM")

#    elif action == '.debug': await message.channel.send(jarvis.debug())
              #Lists everyone's cards. For debug purposes only. Disable before real games if you like.

    elif action == '.gameover':
        await message.channel.send("Game over, man, game over!\nAll characters unassigned, all cards returned, deck shuffled.")
        jarvis.reset()
        pinned = await message.channel.pins()
        for msg in pinned: await msg.unpin()

client.run(TOKEN)
