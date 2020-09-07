# jarvis
Discord bot for Marvel SAGA rpg system

Store DISCORD_TOKEN and DISCORD_GUILD in a .env file in the root folder, and you're good to go.

Note that the bot will only respond to requests on channels listed in the valid_channels list in bot.py. It will otherwise respond with a polite refusal.


**BOT COMMANDS**

You can register a character to yourself with `.register <Character name>`.

You can draw cards to your hand with `.draw <number>`. The bot will message you in private with your cards. If you don't specify a number it defaults to 1.

You can play a card with `.play <index>`, where index is the card index, which you'll find in the bottom left of each card.

You can _show_ a card without playing it with `.show <index>`

You can flip a card from the deck at random with `.flip`. The card is immediately returned to the deck.

You can peek at everyone's hand sizes with `.peek`

You can play a token with `.boost`. If you have tokens, they'll be listed in your hand.

You can release a character with `.deregister`

You can remind yourself of the GM's hand (which is face up) with `.gm`

You can put the game back in the box with `.gameover`, which deregisters all characters, and shuffles all cards back into the deck.


**GM Specific commands:**

You can draw a new narrative card with `.narrative`. The current narrative card will be pinned to the channel.

You can award a player a boost token with `.boost <username>`
