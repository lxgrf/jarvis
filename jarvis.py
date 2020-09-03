# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 18:29:13 2020

@author: apgri
"""

import random
import pandas as pd

hands = {"GM":[], "Narrative":[]} #registers cards to  a character
chars = {} #registers user to a character
drawn_cards = []
discard = []

def register(user, char):
    chars.update({user:char})
    hands.update({char:[]})
    return "{} registered to {}.".format(char, user)

def fromdeck():
    card = False
    while card == False:
        x = random.randrange(96)
        if (x not in drawn_cards): card = x
    return card

def draw(user, number = 1):
    initial = len(hands[chars[user]])
    while len(hands[chars[user]]) < (initial + number):
        x = fromdeck()
        drawn_cards.append(x)
        hands[chars[user]].append(x)
    return "{} has drawn {} cards".format(chars[user], number)

def show(user, card):
    if (card in hands[chars[user]]):
        x = "{} revealed a card:\n{}".format(chars[user], deck.iloc[card]['Link'])
    else: x = "No such card in your hand."
    return x

def play(user, card):
    doom = False
    if (card in hands[chars[user]]):
        hands[chars[user]].remove(card)
        if deck.iloc[card]['Suit'] == "Doom" and chars[user] != "GM":
            hands["GM"].append(card)
            doom = True
        else: drawn_cards.remove(card)
        x = "{} played \n{}.".format(chars[user], deck.iloc[card]['Link'])
        if doom:
            x += "\n\n{} has played a Doom suit card!\nGM's new hand:\n`{}`".format(chars[user], deck.loc[hands["GM"]])
    else: x = "No such card."
    return x

def reset():
    drawn_cards = []
    discard = []
    hands = {"GM":[], "Narrative":[]}
    chars = {}
    print("Reset!")

def flip(narrative = False): 
    new = fromdeck()
    if narrative:
        if len(hands["Narrative"]) > 0:
            old = hands["Narrative"][0]
            hands["Narrative"].remove(old)
            drawn_cards.remove(old)
        hands["Narrative"].append(new)
        drawn_cards.append(new)
    return deck.iloc[new]['Link']

def lose(user, number=1):
    for _ in range(number):
        card = random.choice(hands[chars[user]])
        hands[chars[user]].remove(card)
        drawn_cards.remove(card)
        print("Lost card {}".format(card))

def showhand(user):
    #Text
    return "`{}`".format(deck.loc[hands[chars[user]], "Value":"Calling"]) 
    #Images
    #x = ""
    #for i in hands[chars[user]]:
    #    x += "{}\n".format(deck.iloc[i]['Link'])

def showhandimage(user):
    #x = "Your hand, {}\n".format(users[user])
    x = ""
    for card in hands[chars[user]]:
        x += "{} ".format(deck.iloc[card]['Link'])
#    return "{}".format(deck.loc[hands[users[user]]]['Link'])
    return x

def handsizes():
    x = ""
    for key in hands: 
        x += "{}'s hand size: {}\n".format(key, len(hands[key]))
    return x

def debug():
    x = "Drawn cards = {}\nDiscarded cards = {}\n".format(drawn_cards, discard)
    for key in hands: x+= "{} has {}\n".format(key, hands[key])
    return x

deck = pd.read_csv('deck.csv')
deck.index.name = "Card"
