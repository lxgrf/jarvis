# Jarvis
_A Discord.py bot for Marvel SAGA rpg system_

Store DISCORD_TOKEN and DISCORD_GUILD in a .env file in the root folder, and you're good to go.

Note that the bot will only respond to requests on channels listed in the valid_channels list in bot.py. It will otherwise respond with a polite refusal.

## Bot Commands
- `.register <Character name>`: Register a character to yourself. Abbreviates to `.r`
- `.draw <number>`: Draw cards to your hand. The bot will message you in private with your cards. Defaults to 1. Abbreviates to `.d`
- `.play <index>`: play a card, where index is the card index, which you'll find in the bottom left of each card. Abbreviates to `.p`
- `.show <index>`: _Show_ a card without playing it. Abbreviates to `.s`
- `.flip`: You can flip a card from the deck at random. The card is immediately returned to the deck. Abbreviates to `.f`
- `.peek`: Peek at everyone's hand sizes and token counts.  
- `.boost`: Play a token. If you have tokens, they'll be listed in your hand. Abbreviates to `.b`.
- `.deregister`: Release a character. Folds the character's hand back into the deck. Abbreviates to `.d`
- `.gm`: Remind yourself of the GM's hand (which is face up).
- `.gameover`: Put the game back in the box. Deregisters all characters, and shuffles all cards back into the deck.

## GM Specific commands:
- `.narrative`: Draw a new narrative card. The current narrative card will be pinned to the channel. Abbreviates to `.n`
- `.boost <username>`: Award a player a boost token. Abbreviates to `.b`
