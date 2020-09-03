# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 18:29:13 2020

@author: apgri
"""

import random
import pandas as pd

hands = {"GM":[],} #registers cards to  a character
users = {} #registers user to a character
drawn_cards = []

def register(user, char): 
    users.update({user:char})
    hands.update({char:[]})
    return "{} registered to {}.".format(char, user)

def fromdeck():
    card = False
    while card == False:
        x = random.randrange(96)
        if (x not in drawn_cards): card = x
    return card

def draw(user, number = 1):
    initial = len(hands[users[user]])
    while len(hands[users[user]]) < (initial + number):
        x = fromdeck()
        drawn_cards.append(x)
        hands[users[user]].append(x)
    return "{} has drawn {} cards".format(users[user], number)

def show(hand): print(str(hand))

def play(user, card):
    doom = False
    if (card in hands[users[user]]):
        hands[users[user]].remove(card)
        if deck.iloc[card]['Suit'] == "Doom" and users[user] != "GM":
            hands["GM"].append(card)
            doom = True
        else: drawn_cards.remove(card)
        x = "{} played \n`{}`.".format(users[user], deck.loc[[card]])
        if doom:
            x += "\n\nA player has spent a Doom suit card!\nGM's new hand:\n`{}`".format(deck.loc[hands["GM"]])
            #showhand("GM")
    else: x = "No such card."
    return x

def reset(): 
    drawn_cards = []
    players = {"GM":[],}

def flip(): print(deck.loc[[fromdeck()]])

def lose(hand, number=1):
    for _ in range(number):
        card = random.choice(players[hand])
        players[hand].remove(card)
        drawn_cards.remove(card)
        print("Lost card {}".format(card))

def showhand(user):
    return "`{}`".format(deck.loc[hands[users[user]]])
    
def handsizes():
    for key in players: 
        print("{}'s hand size: {}".format(key, len(players[key])))

deck = pd.read_csv('deck.csv')
