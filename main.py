from utils import game
from discord import Client, Intents, Embed, File
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select_option, create_select
from discord_slash.model import ButtonStyle
import pickle
from os.path import exists
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('Token')

if exists("gamestates.pkl"):
    with open("gamestates.pkl", 'rb') as f:
        games = pickle.load(f)
else:
    games = dict()


def savestate(games):
    with open("gamestates.pkl", 'wb') as w:
        pickle.dump(games, w)


def newgame(name):
    games.update({name: game()})


bot = Client(intents=Intents.all())
slash = SlashCommand(bot, sync_commands=True)


select = create_select(
    options=[
        create_select_option("Strength", value="s", emoji="💪"),
        create_select_option("Agility", value="a", emoji="🤸"),
        create_select_option("Intellect", value="i", emoji="🧠"),
        create_select_option("Willpower", value="w", emoji="❤️"),
        create_select_option("Damage", value="l", emoji="💀")
    ],
    placeholder="Choose your suit",
    min_values=1, # the minimum number of options a user must select
    max_values=1 # the maximum number of options a user can select
)
row_select = create_actionrow(select)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.id not in games.keys():
            newgame(guild.id)
    print(games)  # Do something with each ID


@slash.slash(name="splay", description="Test function for user-friendly suit selection")
async def testplay(ctx: SlashContext, **cards):
    cards = cards['cards'].split(" ")
    embed = Embed(title="Select a suit")
    selectmsg = await ctx.send(embed=embed, components=[row_select])
    while True:
        try:
            # res = await bot.wait_for("select", check=True, timeout=10)
            res = await bot.wait_for("select_option", check=None)
            print(res.values)
            print(res)
            label = res.values[0]

            await res.respond(content=f"You have selected {label}")
            #await selectmsg.delete()

            print(label)  # This was just for checking the output.
            break

        except asyncio.TimeoutError:
            await ctx.send("Sorry, you didn't reply in time!")
            await selectmsg.delete()
            break




@bot.event
async def on_button_click(interaction):
    await interaction.respond(type=6)
    await interaction.author.send("Click")


@slash.slash(name="register", description="Assign a character and join the game.")
async def register(ctx: SlashContext, charname):
    success = games[ctx.guild.id].register(ctx.author.name, charname)
    if success:
        embed = Embed(title="New character registered!", description=f'{ctx.author.name} has registered as {charname}!')
        savestate(games)
        await ctx.author.edit(nick=charname)
    else:
        embed = Embed(title="Registration Error!",
                      description="You already have a character. Please unregister that one first.")
    await ctx.send(embed=embed)


@slash.slash(name="deregister", description="Unassign a character,")
async def deregister(ctx: SlashContext):
    charname = games[ctx.guild.id].users[ctx.author.name]
    games[ctx.guild.id].deregister(ctx.author.name)
    embed = Embed(title="Character unregistered!", description=f'{ctx.author.name} has released {charname}')
    savestate(games)
    await ctx.author.edit(nick="")
    await ctx.send(embed=embed)


@slash.slash(name="peek", description="Report current game state")
async def peek(ctx: SlashContext):
    embed = Embed(title="Current game state for this server:", description=games[ctx.guild.id].report())
    await ctx.send(embed=embed)


@slash.slash(name="draw", description="Draw cards to your hand. Must have a registered character.")
async def draw(ctx: SlashContext, cards: int):
    # Draw cards
    games[ctx.guild.id].draw_to_hand(ctx.author.name, int(cards))
    savestate(games)

    # Update Channel
    total = len(games[ctx.guild.id].hands[ctx.author.name])
    description = f'{ctx.author.nick} drew {cards} cards, making a total hand size of {total}'
    await ctx.send(embed=Embed(title="Cards drawn!", description=description))

    # Update user (by message)
    file = File(games[ctx.guild.id].hand(ctx.author.name), filename="image.jpg")
    description = ""
    if games[ctx.guild.id].tokens[ctx.author.name] >0:
        description += "Boost Tokens: "
        for _ in range(games[ctx.guild.id].tokens[ctx.author.name]):
            description += "⚡"
    embed = Embed(title="Your new hand:", description=description)
    embed.set_image(url="attachment://image.jpg")
    await ctx.author.send(embed=embed, file=file)


@slash.slash(name="play", description="Play cards!")
async def play(ctx: SlashContext, suit, **cards):
    cards = cards['cards'].split(" ")
    response = games[ctx.guild.id].play_cards(user=ctx.author.name, suit=suit, cards=cards)
    savestate(games)
    embed = Embed(title=response["title"], description=response["text"])
    if response["img"]:
        file = File(response["img"], filename="image.jpg")
        embed.set_image(url="attachment://image.jpg")
        await ctx.send(embed=embed, file=file)

        # Update user (by DM)
        file = File(games[ctx.guild.id].hand(ctx.author.name), filename="image.jpg")
        description = ""
        if games[ctx.guild.id].tokens[ctx.author.name] > 0:
            description += "Boost Tokens: "
            for _ in range(games[ctx.guild.id].tokens[ctx.author.name]):
                description += "⚡"
        embed = Embed(title="Your new hand:", description=description)
        embed.set_image(url="attachment://image.jpg")
        await ctx.author.send(embed=embed, file=file)

    else:
        await ctx.send(embed=embed)

    # If a doom card was played, report GM's hand
    if response["doom"]:
        file = File(games[ctx.guild.id].hand("GM"), filename="image.jpg")
        embed = Embed(title="GM's Hand")
        embed.set_image(url="attachment://image.jpg")
        await ctx.send(embed=embed, file=file)

@slash.slash(name="flip", description="Flip a card at random.")
async def flip(ctx: SlashContext):
    response = games[ctx.guild.id].flip()
    savestate(games)
    embed = Embed(title=response["title"], description=response["text"])
    file = File(response["img"], filename="image.jpg")
    embed.set_image(url="attachment://image.jpg")
    await ctx.send(embed=embed, file=file)

@slash.slash(name="GM_hand", description="View the cards in the GM's hand")
async def gm_hand(ctx: SlashContext):
    session = ctx.guild.id
    if games[session].gm and len(games[session].hands[games[session].gm]) > 0:
        file = File(games[session].hand(games[session].gm), filename="image.jpg")
        embed = Embed(title="GM's Hand")
        embed.set_image(url="attachment://image.jpg")
        await ctx.send(embed=embed, file=file)
    else:
        embed = Embed(title="GM's Hand", description="The GM's hand is empty. Perhaps play some Doom cards?")
        await ctx.send(embed=embed)

@slash.slash(name="narrative", description="Draw a new narrative card.")
async def narrative(ctx: SlashContext):
    response = games[ctx.guild.id].narrative(user=ctx.author.name)
    savestate(games)
    embed = Embed(title=response["title"], description=response["text"])
    if response["img"]:
        file = File(response["img"], filename="image.jpg")
        embed.set_image(url="attachment://image.jpg")
        pinned = await ctx.channel.pins()
        for msg in pinned:
            await msg.unpin()
        pinmsg = await ctx.send(embed=embed, file=file)
        await pinmsg.pin()
    else:
        await ctx.send(embed=embed)

@slash.slash(name="GameOver", description="Release all characters, shuffle cards back into deck.")
async def gameover(ctx: SlashContext):
    games[ctx.guild.id].reset()
    savestate(games)
    for member in ctx.guild.members:
        try:
            await member.edit(nick="")
        except:
            pass
    pinned = await ctx.channel.pins()
    for msg in pinned:
        await msg.unpin()
    embed = Embed(title="Game over", description="All characters unassigned, all cards shuffled back into the deck")
    file = File('snap.gif', filename="snap.gif")
    embed.set_image(url="attachment://snap.gif")
    await ctx.send(file=file, embed=embed)

@slash.slash(name="damage", description="Sacrifice cards for damage.")
async def damage(ctx: SlashContext):
    pass

@slash.slash(name="giveBoost", description="GM Only. Assign a boost token to a player.")
async def giveBoost(ctx: SlashContext, target: str):
    targetuser = False
    for key, value in games[ctx.guild.id].users.items():
        if value == target:
            targetuser = key
    if targetuser:
        games[ctx.guild.id].tokens[targetuser] += 1
        savestate(games)
        embed = Embed(title="Token issued!", description=f'A token was issued to {target}!')
    else:
        embed = Embed(title="Token issuing error...", description="No such users found.")
    await ctx.send(embed=embed)

@slash.slash(name="useBoost", description="Use a boost token.")
async def useBoost(ctx: SlashContext):
    if games[ctx.guild.id].tokens[ctx.author.name] > 0:
        games[ctx.guild.id].tokens[ctx.author.name] -= 1
        games[ctx.guild.id].boosted[ctx.author.name] = True
        embed = Embed(title=f'{ctx.author.name} used a Boost!', description="The next (non-Doom) card played is an automatic trump!")
        savestate(games)
    else:
        embed = Embed(title="Boost error", description="You don't have boosts to use...")
    await ctx.send(embed=embed)


@slash.slash(name="override", description="Boost your next play, without a token.\n Useful for world class skills, etc.")
async def override(ctx: SlashContext):
    games[ctx.guild.id].boosted[ctx.author.name] = True
    embed=Embed(title=f'{ctx.author.name} prepares a heroic action!',
                description="The next card played will automatically count as trump!")
    await ctx.send(embed=embed)

bot.run(TOKEN)
