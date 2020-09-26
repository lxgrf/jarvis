# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 17:09:57 2020

@author: apgri
"""

import pandas as pd
from PIL import Image
import random
import pickle

deck = pd.read_csv('deck.csv')
deck.index.name = 'Card'
cards = {*range(len(deck))}

def dump(server, table):
    file = "gamestates/{}".format(server)
    with open(file, 'wb') as f: pickle.dump(table, f)

def retrieve(server):
    file = "gamestates/{}".format(server)
    with open(file, 'rb') as f: table = pickle.load(f)
    return table

def singlecard(table):
    card = random.sample(available(table),1)[0]
    link = deck.iloc[card]['Link']
    return card, link

def available(table):
    drawn = set()
    for a in table['hands'].values(): drawn = drawn.union(a)
    x = cards - drawn
    return x

def register(server, user, character): 
    table = retrieve(server)
    if character == 'Narrative': return "You can't be the Narrative card. Don't be weird."
    if user in table['characters']: return "You are already registered. Unregister first."
    if character in table['characters'].values(): return "Character already registered."
    else:
        if character.upper() == "GM": character = "GM"
        table['characters'].update({user:character})
        table['hands'].update({character:set()})
        table['tokens'].update({character:0})
        dump(server, table)
        return "{} registered to {}".format(character, user)

def deregister(server, user):
    table = retrieve(server)
    if user in table['characters']:
        character = table['characters'][user]
        del table['characters'][user]
        del table['hands'][character]
        if "GM" not in table['hands']: table['hands'].update({"GM":set()})
        dump(server, table)
        return "{} deregistered.".format(character)
    else: return "You cannot deregister. You are not registered."

def boost(server, user, target=False):
    table = retrieve(server)
    if table['characters'][user] == "GM":
        if target and target in table['characters']:
            character = table['characters'][target]
            table['tokens'][character] += 1
            dump(server, table)
            msg = "Token assigned to {}!".format(character)
        else: msg = "Whom did you want to assign a token to?"
    elif user in table['characters']:
        character = table['characters'][user]
        if table['tokens'][character] > 0:
            table['tokens'][character] -= 1
            dump(server, table)
            msg = "{} spent a token!".format(character)
        else: msg = "{} has no tokens to spend.".format(character)
    return msg

def draw(server, user, number=1):
    table = retrieve(server)
    if user in table['characters']:
        newcard = set()
        character = table['characters'][user]
        for _ in range(number): newcard.add(singlecard(table)[0])
        table['hands'][character] = table['hands'][character].union(newcard)
        dump(server, table)
        msg = "{} has drawn {}.".format(character, number)
    else: msg = "Please register a character with '.register <name>' before drawing."
    return msg

def play(server, user, card): #Doom provisions not working brilliantly
    doom = False
    table = retrieve(server)
    if user not in table['characters']: return "Please register a character before drawing cards.", doom
    character = table['characters'][user]
    if card not in table['hands'][character]: return "You do not hold this card.", doom
    if deck.iloc[card]['Suit'] == "Doom" and table['characters'][user] != "GM": 
        table['hands']['GM'].add(card)
        doom = True
    table['hands'][character].remove(card)
    dump(server, table)
    return "{} played \n{}.".format(table['characters'][user], deck.iloc[card]['Link']), doom

def flip(server):
    card, link = singlecard(retrieve(server))
    return link
 
def narrative(server, user):
    table = retrieve(server)
    doom = False
    if table['characters'][user] != "GM": return False, False #Only the GM may draw Narrative
    if len(table['hands']["Narrative"]) > 0: 
        oldcard = table['hands']["Narrative"].pop()
        if deck.iloc[oldcard]['Suit'] == "Doom":
            table['hands']["GM"].add(oldcard)
            doom = True
    card, link = singlecard(table)
    table['hands']['Narrative'].add(card)
    dump(server, table)
    return link, doom
    
def peek(server):
    table = retrieve(server)
    msg = ""
    for key in table['hands']:
        if len(table['hands'][key])==0: msg += "{} has no cards.\n".format(key)
        else: msg += "{}'s hand size: {}\n".format(key, len(table['hands'][key]))
    for key in table['tokens']: msg += "{} has {} tokens.\n".format(key, table['tokens'][key])
    return msg

def handimage(server, user):
    table = retrieve(server)
    gm = False
    if user in table['characters']:
        gm = (table['characters'][user] == "GM")
    if user == "GM": 
        gm = True
        character = "GM"
    else:
        character = table['characters'][user]
    held = sorted(table['hands'][character])
    files = []
    if len(held)>0:
        for card in held: files.append("cards/ncard_{}.jpg".format(card)) #Get relevant image files
        images = [Image.open(x) for x in files] #Open all files
        widths, heights = zip(*(i.size for i in images)) #Get all file widths and heights
        max_height = max(heights) #Find heighest height
        total_width = sum(widths) #Find total width
        x_offset = 0
        new_im = Image.new('RGB', (total_width, max_height)) #Create new image based on calculated dimensions
        for im in images:
            new_im.paste(im, (x_offset, 0)) 
            x_offset += im.size[0] #Paste images in, reset starting point to cumulative x position
        file = 'hands/{}_hand.jpg'.format(user) #Name for user 
        new_im.save(file) #and save
    else: file = False 
    tokens = False
    if user in table['tokens']:
        tokens = ""
        for _ in range(table['tokens'][user]): tokens += ":zap:"
    return file, gm, tokens
