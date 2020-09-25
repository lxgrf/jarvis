# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 20:42:58 2020

@author: apgri
"""

import os
import discord
from dotenv import load_dotenv
from utils import draw, register, deregister, handimage, play, flip, narrative, boost
import pickle

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

async def hand(server, message, user):
    imagefile, GM, tokens = handimage(server, user)
    if imagefile:
        if GM: 
            title = "GM's Hand"
            description = ""
        else: 
            title = "Your Hand"
            description = "Card index numbers are in the bottom left of each card."
            if tokens: description += "\nTokens: {}".format(tokens)
        embed = discord.Embed(title=title, description=description, color=0x0ff00)
        file = discord.File(imagefile, filename = "image.jpg")
        embed.set_image(url="attachment://image.jpg")
        if GM: await message.channel.send(file=file, embed=embed)
        else: await message.author.send(file=file, embed=embed)

@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds)
    print("{} is connected to guild {}.".format(client.user, guild.id))
    
@client.event
async def on_message(message):
    if message.author == client.user: # Stop the bot from replying to itself
        return
    if message.guild is None: # Stops the bot from replying to PMs
        await message.author.send("Unfortunately I cannot act on commands sent by PM.")
        return
    
    server = str(message.guild.id)
    user = message.author.name
    
    if not os.path.exists("gamestates/{}".format(server)):
        table = {'hands':{'GM':set(),
                          'Narrative':set()}, 
                'characters':dict(),
                'tokens':dict()}
        with open("gamestates/{}".format(server), 'wb') as f: pickle.dump(table, f)

    command = message.content.split(" ")
    action = command[0] # Extract first word to check against commands

    if action in [".draw", ".d", ".dr"]:
        try: msg = draw(server, user, int(command[1]))
        except: msg = draw(server, user)
        await message.channel.send(msg)
        await hand(server, message, user)
    
    elif action in [".register", ".r", ".reg"]:
        if len(command)<2: await message.channel.send("Register what?")
        else: await message.channel.send(register(server, user, " ".join(command[1:])))
        
    elif action == ".deregister": await message.channel.send(deregister(server, user))
    
    elif action in [".play", ".p"]:
        try: msg, doom = play(server, user, int(command[1]))
        except: 
            msg = "Which card do you wish to play?"
            doom = False
        await message.channel.send(msg)
        await hand(server, message, user)
        if doom: 
            await message.channel.send("A doom card has been played!")
            await hand(server, message, user="GM")
    
    elif action in [".flip", ".f"]: await message.channel.send("**Random card from deck**\n{}".format(flip(server)))
    
    elif action in [".narrative", ".n"]:
        card, doom = narrative(server, user)
        if card == False: await message.channel.send("Only the GM may draw Narrative cards.")
        else:
            pinned = await message.channel.pins()
            for msg in pinned: await msg.unpin()
            pinmsg = await message.channel.send("***Narrative Card***\n{}".format(card))
            await pinmsg.pin()
            if doom:
                await hand(server, message, user="GM")
                
    elif action in [".boost", ".b"]:
        try: msg = boost(server, user, command[1])
        except: msg = boost(server, user)
        await message.channel.send(msg)
            
    elif action == ".debug":
        with open("gamestates/{}".format(server), 'rb') as f: x = pickle.load(f)
        await message.channel.send(x)
    
    elif action == '.gameover':
        pinned = await message.channel.pins()
        for msg in pinned: await msg.unpin()
        embed = discord.Embed(title="Game over", description="All characters unassigned, all cards returned, deck shuffled", color=0x0ff00)
        file = discord.File('snap.gif', filename = "snap.gif")
        embed.set_image(url="attachment://snap.gif")
        await message.channel.send(file=file, embed=embed)
        tablestate = 'gamestates/{}'.format(server)
        if os.path.exists(tablestate): os.remove(tablestate)
    
client.run(TOKEN)