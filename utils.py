import pandas as pd
import random
from PIL import Image


class game:
    card_details = pd.read_csv('deck.csv')
    card_details.index.name = 'Card'
    cards = {*range(len(card_details))}
    suits = {'s': 'Strength', 'a': 'Agility', 'i': 'Intellect', 'w': 'Willpower', 'l': 'Damage', 'd': 'Damage'}
    gm = ""

    def __init__(self):
        self.users = dict()  # user : character
        self.hands = {
                        "Narrative": set(),
                        "Discard": set()
                    }
        self.tokens = dict()
        self.boosted = dict()

    def register(self, user, character):
        if user not in self.users.keys():
            self.users.update({user: character})
            self.hands.update({user: set()})
            self.tokens.update({user: 0})
            self.boosted.update({user: False})
            if character.upper() == "GM":
                self.gm = user
            return True
        else:
            return False

    def deregister(self, user):
        if self.users[user] == self.gm:
            self.gm = ""
        del self.users[user]
        self.hands["Discard"].update(self.hands[user])
        del self.hands[user]
        del self.tokens[user]
        del self.boosted[user]

    def reset(self):
        self.users = dict()  # user : character
        self.hands = {
                        "Narrative": set(),
                        "Discard": set()
                    }
        self.tokens = dict()

    def report(self):
        x = f'{self.users}\n\n{self.hands}\n\n{self.tokens}'
        print(x)
        return x

    def draw_to_hand(self, user, n=1):
        if n > 5:
            n = 5
        self.hands[user].update(self.draw_cards(n))

    def draw_cards(self, n):
        unavailable = set()
        for hand in self.hands.values():
            unavailable.update(hand)
        available = self.cards - unavailable

        if len(available) <= n:
            print("Resetting Discard...")
            available.update(self.hands["Discard"])
            self.hands["Discard"] = set()

        return set(random.sample(available, n))

    def play_cards(self, user, cards: list, suit=False):
        #boost = self.boosted[user]
        #boost = False
        #self.boosted[user] = False

        if suit is not None:
            suit = self.suits[suit.lower()[0]]
        cards = [int(card) for card in cards]
        total = 0
        response = {"title": "", "text": "", "img": False, "doom": False}

        # Scoop up the Doom.
        if self.gm != user and suit != "Damage":
            for card in cards:
                if self.card_details.iloc[card]['Suit'] == 'Doom':
                    self.hands[self.gm].update({card})
                    response['text'] += "The Doom pool grows...\n\n"
                    response["doom"] = True

        if all([card in self.hands[user] for card in cards]):
            response['title'] = f'{self.users[user]} played a card!'
            for card in cards:
                total += int(self.card_details.iloc[card]['Value'])
            cardsuit = self.card_details.iloc[cards[-1]]['Suit']
            if (self.boosted[user] and cardsuit != 'Doom') or cardsuit == suit:
                self.boosted[user] = False
                while True:
                    river = self.draw_cards(1).pop()
                    if river in cards:
                        continue
                    cards.append(river)
                    total += int(self.card_details.iloc[river]['Value'])
                    print(total)
                    if self.card_details.iloc[river]['Suit'] != suit:
                        break

            response['text'] += f'Played cards total value: {total}\n'
            for c in cards:
                self.hands[user].discard(c)
                self.hands["Discard"].add(c)
            response['img'] = self.imggen(user, cards)
        else:
            response['title'] = 'Error'
            response['text'] = 'You do not hold all the cards you have tried to play.'
        return response

    def get_users(self):
        return self.users

    def flip(self):
        card = self.draw_cards(1).pop()
        aura = self.card_details.iloc[card]['Aura']
        response = {"title": "Flipped Card", "text": f"Aura = {aura}", "img": f'cards/ncard_{card}.jpg'}
        self.hands["Discard"].add(card)
        return response

    def narrative(self, user):
        response = {"title": "", "text": "", "img": ""}
        if self.gm == user:
            if self.hands["Narrative"]:  # Discard existing hand
                self.hands["Discard"].update(self.hands["Narrative"])
                self.hands["Narrative"] = set()
            card = self.draw_cards(1).pop()
            self.hands["Narrative"].add(card)
            aura = self.card_details.iloc[card]['Aura']
            value = self.card_details.iloc[card]['Value']
            calling = self.card_details.iloc[card]['Calling']
            event = self.card_details.iloc[card]['Event']
            response['title'] = 'New Narrative Card!'
            response['text'] = f'Aura = {aura}\nValue = {value}\nCalling = {calling}\nEvent = {event}'
            response['img'] = f'cards/ncard_{card}.jpg'
        else:
            response['title'] = 'Error'
            response['text'] = 'Only the GM may draw Narrative cards.'
        return response

    def hand(self, user):
        if user == "GM":
            user = self.gm
        handcards = self.hands[user]
        file = self.imggen(user, sorted(handcards))
        return file

    def imggen(self, user, cards):
        images = [Image.open(f'cards/ncard_{card}.png') for card in cards]
        # images = [Image.open(x) for x in files]  # Open all files
        widths, heights = zip(*(i.size for i in images))  # Get all file widths and heights
        max_height = max(heights)  # Find highest height
        total_width = sum(widths)  # Find total width
        x_offset = 0
        new_im = Image.new('RGB', (total_width, max_height))  # Create new image based on calculated dimensions
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]  # Paste images in, reset starting point to cumulative x position
        file = f'hands/{user}_hand.png'  # Name for user
        new_im.save(file)  # and save
        return file
