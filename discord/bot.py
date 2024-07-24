import base64
import io
import os
import random
import sys
import time
import urllib

import discord
import django
import requests

from datetime import datetime, timedelta

from discord.ext import commands
from discord.utils import get

from constants import (
    WOZZT_URL, COOLDOWN_MESSAGE, HELP, SCROLL_TOP, SCROLL_BOTTOM, PROGRAMS_TEXT, EDITORS_TEXT, RESOURCES_TEXT, WORLDS_TEXT, INVALID_LINK_TEXT, LINKS
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import Scroll  # noqa: E402

TOKEN = os.environ.get("MOZ_DISCORD_BOT_TOKEN", "-UNDEFINED-")
SERVER = None
PUBLIC_ROLES = [
    "ZZTer", "MZXer", "He/Him", "She/Her", "It/Its", "They/Them",
    "Stream-Alerts-Asie", "Stream-Alerts-Dos", "Stream-Alerts-Meap", "Stream-Alerts-All"
]
COMMANDS = ["addrole", "help", "removerole", "scroll", "zzt", "vouch", "link", "links", "live",]
CHANNELS = []
LAST_TIME = {
    "addrole": 0,
    "link": 0,
    "links": 0,
    "live": 0,
    "removerole": 0,
    "scroll": 0,
    "zzt": 0,
    "help": 0,
    "vouch": 0,
}

SCROLLS = list(Scroll.objects.filter(published=True).order_by("id"))


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")  # Roll our own


def check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN):
    NOW = int(time.time())
    author = ctx.message.author.name + "#" + ctx.message.author.discriminator
    command = str(ctx.command)
    time_diff = NOW - LAST_TIME[command]

    if VALID_ROOMS and ctx.channel.name not in VALID_ROOMS:
        return {"SUCCESS": False, "REASON": "Invalid room", "RESPONSE": ""}
    if VALID_USERS and author not in VALID_USERS:
        return {"SUCCESS": False, "REASON": "Invalid user", "RESPONSE": ""}
    if COOLDOWN:
        if time_diff < COOLDOWN:
            time_remaining = COOLDOWN - time_diff
            return {
                "SUCCESS": False,
                "REASON": "Cooldown limited",
                "RESPONSE": COOLDOWN_MESSAGE.format(command, time_remaining)
            }
    LAST_TIME[command] = int(NOW)
    return {"SUCCESS": True, "REASON": "", "RESPONSE": ""}


@bot.command(help="Add a role. (Roles: {})".format(", ".join(PUBLIC_ROLES)))
async def addrole(ctx, *args):
    VALID_ROOMS = ("bots", "bot-dev", "welcome")
    VALID_USERS = ()
    COOLDOWN = 0

    requested_roles = args
    to_add = []

    for r in requested_roles:
        for public_role in PUBLIC_ROLES:
            if r.lower() == public_role.lower():
                to_add.append(public_role)

    if not to_add:
        return False

    status = check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN)
    if status["SUCCESS"]:
        member = ctx.message.author

        new_roles = []
        for r in to_add:
            new_roles.append(get(ctx.guild.roles, name=r))
        await member.add_roles(*new_roles)
        await ctx.send("Your roles have been updated! (Added: {})".format(", ".join(to_add)))
    else:
        print(status.get("REASON"))
        if status.get("RESPONSE"):
            await ctx.send(status["RESPONSE"])


@bot.command(help="Vouch for another user. (Syntax: !vouch USERNAME)")
async def vouch(ctx, *args):
    VALID_ROOMS = ("bot-dev", "welcome")
    VALID_USERS = ()
    COOLDOWN = 0

    status = check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN)

    # Also check the user is allowed to do this
    joined = ctx.author.joined_at
    now = datetime.now()
    delta = timedelta(days=90)
    diff = now - delta

    if str(diff) < str(joined):
        await ctx.send(
            "Your account does not have permission to vouch for others yet."
        )
        return False

    vouched_username = " ".join(args)
    vouched_user = None

    if ctx.author.name.lower() == vouched_username.lower():
        await ctx.send(
            "You cannot vouch for yourself!"
        )
        return False

    matched = False
    for u in bot.get_all_members():
        if u.name.lower() == vouched_username.lower():
            matched = True
            vouched_user = u
            break

    if not matched:
        await ctx.send(
            "Sorry, no such user was found."
        )
    else:
        await vouched_user.add_roles(get(ctx.guild.roles, name="Veryspecial"))
        await ctx.send("`{}` has been vouched for!".format(vouched_user.name))


@bot.command()
async def help(ctx):
    VALID_ROOMS = ("bots", "bot-dev", "welcome")
    VALID_USERS = ()
    COOLDOWN = 0

    status = check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN)
    if status["SUCCESS"]:
        await ctx.send(HELP)


@bot.command()
async def link(ctx, category="?"):
    VALID_ROOMS = ("bots", "bot-dev", "welcome", "zzt", "zzt-worlds", "zzt-programs", "zzt-bugs")
    VALID_USERS = ()
    COOLDOWN = 0
    status = check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN)
    if status["SUCCESS"]:
        await ctx.send(LINKS.get(category.lower(), INVALID_LINK_TEXT))

@bot.command()
async def links(ctx, category="?"):
    await link(ctx, category)


@bot.command()
async def live(ctx, category="?"):
    VALID_ROOMS = ("bot-dev", "announcements",)
    VALID_USERS = ("Dos#0079")
    COOLDOWN = 0

    status = check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN)
    if status["SUCCESS"]:
        await ctx.send("Now streaming on https://twitch.tv/worldsofzzt")


@bot.command(help="Remove a role. (Roles: {})".format(", ".join(PUBLIC_ROLES)))
async def removerole(ctx, *args):
    VALID_ROOMS = ("bots", "bot-dev", "welcome")
    VALID_USERS = ()
    COOLDOWN = 0

    requested_roles = args
    to_add = []

    for r in requested_roles:
        for public_role in PUBLIC_ROLES:
            if r.lower() == public_role.lower():
                to_add.append(public_role)

    if not to_add:
        return False

    status = check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN)
    if status["SUCCESS"]:
        member = ctx.message.author

        new_roles = []
        for r in to_add:
            new_roles.append(get(ctx.guild.roles, name=r))
        await member.remove_roles(*new_roles)
        await ctx.send("Your roles have been updated! (Removed: {})".format(", ".join(to_add)))
    else:
        print(status.get("REASON"))
        if status.get("RESPONSE"):
            await ctx.send(status["RESPONSE"])


@bot.command(help="Some reading material. (10 sec cooldown)")
async def scroll(ctx, idx="?"):
    VALID_ROOMS = ("bots", "bot-dev")
    VALID_USERS = ()
    COOLDOWN = 10

    request = False
    if idx != "?":
        try:
            idx = int(idx)
            request = True
        except ValueError:
            idx = "?"

    status = check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN)
    if status["SUCCESS"]:
        scroll = None
        if request and idx <= len(SCROLLS):
            scroll = SCROLLS[idx - 1]

        if not scroll:
            idx = random.choice(range(0, len(SCROLLS)))
            scroll = SCROLLS[idx]

        render = scroll.render_for_discord()
        await ctx.send(render + "*Source: <https://museumofzzt.com{}>*".format(scroll.source))
    else:
        print(status.get("REASON"))
        if status.get("RESPONSE"):
            await ctx.send(status["RESPONSE"])


@bot.command(help="Posts a random ZZT board. (15 sec cooldown)")
async def zzt(ctx):
    VALID_ROOMS = ("worlds-of-zzt-feed", "bots", "bot-dev")
    VALID_USERS = ()
    COOLDOWN = 15
    params = ()

    status = check_permissions(ctx, VALID_ROOMS, VALID_USERS, COOLDOWN)
    if status["SUCCESS"]:
        resp = requests.get(WOZZT_URL, params=params)
        if resp.status_code == 200:
            data = resp.json()["data"]
            discord_post = "**{}** by {} ({})\n"
            if data["file"]["company"]:
                discord_post += "Published by: {}\n".format(data["file"]["company"])
            discord_post += "`[{}] - \"{}\"` \n"
            discord_post += "Explore: <{url}?file={f}&board={b}>\n".format(
                url=data["museum_link"].replace(" ", "%20%"),
                f=urllib.parse.quote(data["world"]),
                b=str(data["board"]["number"])
            )

            if data["file"]["archive_name"]:
                discord_post += ("Play: <{}>".format(data["play_link"]))

            discord_post = discord_post.format(
                data["file"]["title"], ", ".join(data["file"]["author"]),
                str(data["file"]["release_date"])[:4], data["world"],
                data["board"]["title"]
            )

            image = io.BytesIO(base64.b64decode(data["b64_image"]))
            await ctx.send(
                discord_post,
                file=discord.File(image, filename="wozzt.png")
            )
        else:
            print("ERROR:")
            print(WOZZT_URL, "raised status", resp.status_code)
    else:
        print(status.get("REASON"))
        if status.get("RESPONSE"):
            await ctx.send(status["RESPONSE"])


@bot.event
async def on_ready():
    print(bot.guilds)
    SERVER = bot.guilds[0]
    for channel in bot.get_all_channels():
        CHANNELS.append(channel)
    print("Worlds of ZZT Bot is ready.")
    print("SERVER:", SERVER.name)
    print("CHANNELS:")
    for c in CHANNELS:
        print("\t", c.name)

bot.run(TOKEN)

"""
    print("AUTHOR")
    print(ctx.message.author)
    print("==="*20)
    print("AUTHOR ROLES")
    print(ctx.message.author.roles)
    print("==="*20)

    print("CHANNEL")
    print(ctx.channel)
    print("==="*20)
    await ctx.send(ADVICE)
"""
