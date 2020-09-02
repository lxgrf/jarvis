# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 18:29:13 2020

@author: apgri
"""

import random
import pandas as pd

players = {"GM":[],}
drawn_cards = []

def register(name): 
    players.update({name:[]})
    return "{} registered.".format(name)

def fromdeck():
    card = False
    while card == False:
        x = random.randrange(96)
        if (x not in drawn_cards): card = x
    return card

def draw(hand, number = 1):
    initial = len(players[hand])
    while len(players[hand]) < (initial + number):
        x = fromdeck()
        drawn_cards.append(x)
        players[hand].append(x)
    print("{} cards drawn".format(number))

def show(hand): print(str(hand))

def play(hand, card):
    doom = False
    if (card in players[hand]):
        players[hand].remove(card)
        if deck.iloc[card]['Suit'] == "Doom" and hand != "GM": 
            players["GM"].append(card)
            doom = True
        else: drawn_cards.remove(card)
        print("{} played \n{}.".format(hand, deck.loc[[card]])) 
        if doom: 
            print("\nA player has spent a Doom suit card!")
            showhand("GM")
    else: print("No such card.")
    
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

def showhand(hand):
    print("{}'s hand:".format(hand))
    print(deck.loc[players[hand]])
    
def handsizes():
    for key in players: 
        print("{}'s hand size: {}".format(key, len(players[key])))

deck = pd.read_csv('deck.csv')