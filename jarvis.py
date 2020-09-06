# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 18:29:13 2020

@author: apgri
"""

import random
import pandas as pd
from PIL import Image

deck = pd.read_csv('deck.csv')
deck.index.name = 'Card'

cards = {*range(len(deck))}
hands = {"GM":set(), "Narrative":set()} #registers cards to  a character
chars = dict() #registers user to a character
boosts = dict()

def register(user, char):
    if user not in chars:
        if char == "Narrative": x = "You can't be the Narrative card. Don't make this weird."
        else:
            chars.update({user:char})
            hands.update({char:set()})
            boosts.update({user:0})
            x = "{} registered to {}.".format(char, user)
    else: x = "You already have a character. You can't have TWO characters. Release your hold on {} with the command .deregister".format(chars[user])
    return x

def deregister(user):
    if user in chars:
        x = "{} released. All cards returned.".format(chars[user])
        if chars[user] != "GM": del hands[chars[user]]
        del chars[user]
        del boosts[user]
    else: x = "You can't deregister. You aren't registered. What would be the point?"
    return x

def boost(user, target = None):
    if chars[user] == "GM":
        if target is not None and target in boosts:
            boosts[target] += 1
            x = "Token assigned to {}, who now has {}.".format(chars[target], boosts[target])
        else: x = "Who do you want to assign a token to?"
    elif user in boosts:
        if boosts[user] > 0:
            boosts[user] -= 1
            x = "{a} played a token! {a} has {b} tokens remaining.".format(a = chars[user], b = boosts[user])
        else: x = "You have no tokens to play!"
    else: x = "Please register a character with .register <name>"
    return x

def fromdeck():
    drawn = set()
    for a in hands.values(): drawn.update(a)
    return random.sample(cards - drawn, 1)[0]

def draw(user, number = 1):
    x = ""
    if user in chars:
        for _ in range(number): hands[chars[user]].add(fromdeck())
        x = "{} has drawn {} card(s)".format(chars[user], number)
    else: x = "You must register a character (with .register <name>) before drawing a card."
    return x

def show(user, card):
    if (card in hands[chars[user]]):
        x = "{} revealed a card without playing it:\n{}".format(chars[user], deck.iloc[card]['Link'])
    else: x = "No such card in your hand."
    return x

def play(user, card):
    doom = False
    y = ""
    if (card in hands[chars[user]]):
        hands[chars[user]].remove(card)
        if deck.iloc[card]['Suit'] == "Doom" and chars[user] != "GM":
            hands["GM"].add(card)
            doom = True
        x = "{} played \n{}.".format(chars[user], deck.iloc[card]['Link'])
        if doom:
            y = "\n\n{} has played a Doom suit card!\nGM's new hand:\n`{}`".format(chars[user], deck.loc[hands["GM"], "Value":"Calling"])
    else: x = "No such card."
    return x, y

def reset(): #There's a better way to do this. Involving classes. Look into that.
    global hands
    global chars
    global boost
    hands = {"GM":set(), "Narrative":set()}
    chars, boosts = dict(), dict()
    print("Reset!")

def flip(narrative = False):
    new = fromdeck()
    if narrative:
        hands["Narrative"].clear()
        hands["Narrative"].add(new)
    return deck.iloc[new]['Link']

def lose(user, number=1):
    for _ in range(number):
        card = random.choice(hands[chars[user]])
        hands[chars[user]].remove(card)
        print("Lost card {}".format(card))

def showhand(user="GM"):
    #Text
    x = ""
    if user == "GM": 
        x = "`{}`".format(deck.loc[hands[user], "Value":"Calling"]) 
    else:
#        x = "`{}`".format(deck.loc[hands[chars[user]], "Value":"Calling"])
        for i in hands[chars[user]]: x += "{} ".format(deck.iloc[i]['Link'])
        if boosts[user]>0:
            x += "\nBoost Tokens: "
            for _ in range(boosts[user]): x+= ":zap:"
    return x
    #Images
    #x = ""
    #for i in hands[chars[user]]:
    #    x += "{}\n".format(deck.iloc[i]['Link'])
    #    return x

def handsizes():
    x = ""
    for key in hands:
        if len(hands[key])==0: x+= "{} has no cards.\n".format(key)
        else: x += "{}'s hand size: {}\n".format(key, len(hands[key]))
    for key in boosts: x+= "{} has {} tokens.".format(chars[key], boosts[key])
    return x

def debug():
    x = ""
    for key in hands:
        x+= "{} has {}\n".format(key, hands[key])
    for key in boosts:
        x+= "{} has {} tokens\n".format(chars[key], boosts[key])
    return x

def handimage(user):
    held = sorted(hands[chars[user]])
    files = []
    for card in held: files.append("cards/ncard_{}.jpg".format(card))
    print(held)
    print(files)
    images = [Image.open(x) for x in files]
    widths, heights = zip(*(i.size for i in images))
    max_height = max(heights)
    total_width = sum(widths)
    x_offset = 0
    new_im = Image.new('RGB', (total_width, max_height))
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]
    x = '{}_hand.jpg'.format(user)
    new_im.save(x)
    return x
