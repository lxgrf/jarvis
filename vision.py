# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 20:42:58 2020

@author: apgri
"""

import os
import discord
from dotenv import load_dotenv
from utils import draw, register, deregister, handimage, play, flip, narrative, boost, peek, suitplay
import pickle

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

blank = {'hands':{'GM':set(),
                  'Narrative':set()}, 
        'characters':dict(),
        'tokens':dict()}

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

async def sendimg(message, title, description, image):
        embed = discord.Embed(title=title, description = description, color=0x0ff00)
        file = discord.File(image, filename = "image.jpg")
        embed.set_image(url="attachment://image.jpg")
        await message.channel.send(file=file, embed=embed)
        
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
        with open("gamestates/{}".format(server), 'wb') as f: pickle.dump(blank, f)
        await message.channel.send("Jarvis is online. Please send `.help` to see relevant commands.")

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
    
#    elif action in [".play", ".p"]:
#        try: 
#            msg, doom = play(server, user, int(command[1]))
#        except: 
#            msg = "Which card do you wish to play?"
#            doom = False
#        await message.channel.send(msg)
#        await hand(server, message, user)
#        if doom: 
#            await message.channel.send("A doom card has been played!")
#            await hand(server, message, user="GM")
    
#    elif action in [".agility", ".a", ".ag", ".agi", ".strength", ".st", ".str", ".s", ".intellect", ".int", ".i", ".willpower", ".will", ".wi", ".w", ".play", ".p", ".pl"]:
    elif (action[:2] in [".s",".a",".i",".w"]) or action in [".play", ".p", ".pl"]:
        suit = action[1]
        cards = command[1:]
        try: 
            title, description, image, doom = suitplay(server, user, suit, cards)
            if not title: await message.channel.send(description) # Returns error messages from suitplay function
            else: await sendimg(message, title, description, image) # Sends successful results
        except:
            await message.channel.send("Which card did you wish to play?")
            doom = False
        await hand(server, message, user) #Send updated hand details
        if doom:
            await message.channel.send("A doom card has been played!")
            await hand(server, message, user="GM")
    
    elif action in [".flip", ".f"]: await message.channel.send("**Random card from deck**\n{}".format(flip(server)))
    
    elif action in [".narrative", ".n"]:
        card, doom = narrative(server, user)
        if card == False: await message.channel.send("Only the GM may draw Narrative cards.")
        else:
            pinned = await message.channel.pins()
            for msg in pinned: 
                if msg.author == client.user: await msg.unpin()
            pinmsg = await message.channel.send("***Narrative Card***\n{}".format(card))
            await pinmsg.pin()
#            if doom:
#                await hand(server, message, user="GM")
                
    elif action in [".boost", ".b"]:
        try: msg = boost(server, user, command[1])
        except: msg = boost(server, user)
        await message.channel.send(msg)
            
    elif action in [".peek", ".pk"]:
        await message.channel.send(peek(server))
        
    elif action == ".gm": await hand(server, message, user="GM")
        
    elif action == ".debug":
        with open("gamestates/{}".format(server), 'rb') as f: x = pickle.load(f)
        await message.channel.send(x)
        
#    elif action == ".debugt":
#        suit = "i"
#        cards = command[1:]
#        title, description, image, doom = suitplay(server, user, suit, cards)
#        await sendimg(message, title, description, image)

    elif action == '.gameover':
        pinned = await message.channel.pins()
        for msg in pinned: 
            if msg.author == client.user: await msg.unpin()
        embed = discord.Embed(title="Game over", description="All characters unassigned, all cards returned, deck shuffled", color=0x0ff00)
        file = discord.File('snap.gif', filename = "snap.gif")
        embed.set_image(url="attachment://snap.gif")
        await message.channel.send(file=file, embed=embed)
        tablestate = 'gamestates/{}'.format(server)
        if os.path.exists(tablestate): os.remove(tablestate)
        with open("gamestates/{}".format(server), 'wb') as f: pickle.dump(blank, f)
        
    elif action in [".help", ".h"]:
        await message.channel.send("`.register <Character name>`: Register a character to yourself. Abbreviates to `.r`\n`.draw <number>`: Draw cards to your hand. The bot will message you in private with your cards. Defaults to 1. Abbreviates to `.d`\n`.play <index>`: play a card, where index is the card index, which you'll find in the bottom left of each card. Abbreviates to `.p`\n`.intellect`, `.strength`, `.agility`, `.willpower <card>`: Plays the stated cards as a card of that trump suit, and continues drawing until no longer trump. Abbreviates to any reasonable shortening.\n`.show <index>`: _Show_ a card without playing it. Abbreviates to `.s`\n`.flip`: You can flip a card from the deck at random. The card is immediately returned to the deck. Abbreviates to `.f`\n`.peek`: Peek at everyone's hand sizes and token counts.  \n`.boost`: Play a token. If you have tokens, they'll be listed in your hand. Abbreviates to `.b`.\n`.deregister`: Release a character. Folds the character's hand back into the deck. Abbreviates to `.d`\n`.gm`: Remind yourself of the GM's hand (which is face up).\n\n`.gameover`: Put the game back in the box. Deregisters all characters, and shuffles all cards back into the deck.\n\nGM Specific commands:\n`.narrative`: Draw a new narrative card. The current narrative card will be pinned to the channel. Abbreviates to `.n`\n`.boost <username>`: Award a player a boost token. Abbreviates to `.b`")
    
client.run(TOKEN)