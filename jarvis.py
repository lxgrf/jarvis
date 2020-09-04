# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 18:29:13 2020

@author: apgri
"""

import random
import pandas as pd

deck = pd.read_csv('deck.csv')
deck.index.name = 'Card'

cards = {*range(len(deck))}
hands = {"GM":set(), "Narrative":set()} #registers cards to  a character
chars = {} #registers user to a character

def register(user, char):
    if user not in chars:
        if char == "Narrative": x = "You can't be the Narrative card. Don't make this weird."
        else:
            chars.update({user:char})
            hands.update({char:set()})
            x = "{} registered to {}.".format(char, user)
    else: x = "You already have a character. You can't have TWO characters. Release your hold on {} with the command .deregister".format(chars[user])
    return x

def deregister(user):
    if user in chars:
        x = "{} released. All cards returned.".format(chars[user])
        if chars[user] != "GM": del hands[chars[user]]
        del chars[user]
    else: x = "You can't deregister. You aren't registered. What would be the point?"
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
    hands = {"GM":set(), "Narrative":set()}
    chars = {}
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
    if user == "GM": 
        return "`{}`".format(deck.loc[hands[user], "Value":"Calling"]) 
    else: 
        return "`{}`".format(deck.loc[hands[chars[user]], "Value":"Calling"])
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
    return x

def debug():
    x = ""
    for key in hands: x+= "{} has {}\n".format(key, hands[key])
    return x
