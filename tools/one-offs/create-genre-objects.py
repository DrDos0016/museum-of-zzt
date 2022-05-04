import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

GENRES = {
    "24HoZZT": "Files containing content created for \"24 Hours of ZZT\" contests where entrants had 24 hours to create a ZZT game adhering to a given topic.",
    "Action": "Files containing content with a strong focus on fighting enemies, usually with shooting being a primary means of attack.",
    "Adventure": "Files containing content in which protagonist(s) go on a journey to accomplish a goal.",
    "Advertisement": "Files containing previews for (then) unreleased ZZT worlds.",
    "Arcade": "Files containing content that generally involves trying to set a high score/fast time.",
    "Art": "Files containing content meant to be experienced more than played.",
    "Beta": "Files containing content that is generally feature complete, but not yet fully tested or publically released (until now)",
    "BKZZT": "Files containing content created for \"Blitzkrieg ZZT\" contests where entrants typically had 30 minutes to 1 hour to create a ZZT game adhering to a given topic.",
    "Cameo": "Files containing content that prominently features members of the ZZT and/or adjacent communities as characters.",
    "Catalog": "Files containing content that provides overviews of other releases from the file's author and/or company.",
    "Cinema": "Files containing content that is meant to be watched more than it is to be played.",
    "Comedy": "Files containing content that is <i>intended</i> to make the player laugh. This genre is intended more for files that focus on humor as one of the more important aspects of itself. No promises that these files are funny now, or were even all that funny when they were brand new.",
    "Comic": "Files containing content presented in a format similar to a comic strip.",
    "Collaboration": "Files containing content where many authors worked together to create the finished product.",
    "Compilation": "Files containing multiple releases of one or more ZZT worlds bundled in a single package.",
    "Contest": "Files containing content created for a content. See 24HoZZt, BKZZT, Game Jam, Ludum Dare, and WoZZT genres for specific contests.",
    "Demo": "Files containing publically released and incomplete content to promote an upcoming world before its completion.",
    "Dungeon": "Files containing content that typically involves traversing dungeons or dungeon-like environments.",
    "Edutainment": "Files containing content intended to be educational and entertaining.",
    "Engine": "Files containing content showcasing a unique type of gameplay via the use of ZZT's objects. This may be a full game, or a proof-of-concept demonstrating a single useage of the engine. Common types of engines such as shooters, platformers, RPGs, etc. have their own dedicated genres as well.",
    "Experimental": "Files containing content that is unconventional when compared to more typical files.",
    "Fangame": "Games which use characters and settings from other media. These may be conversions of non-ZZT games or wholly original works.",
    "Fantasy": "Games which make heavy use of fantasy themes, settings, and imagery.",
    "Fighting": "Games which involve opponents ",
    "Font": "Files which contain custom fonts to be used for ZZT worlds. Not games which <i>use</i> fonts which are marked by having a detail of \"Modified Graphics\".",
    "Help": "Files containing content to help the user learn how to play or create things with ZZT.",
    "Horror": "Files containing content to make the user feel afraid.",
    "Incomplete": "Files which have been released in an incomplete state, typically due to the author's abandonment.",
    "Ludum Dare": "Files containing content created for the Ludum Dare compeition. Entrants have either 48 or 72 hours to create a game adhering to a topic.",
    "Magazine": "Files containing content with a strong focus on text you would find in a (typically video game focused) magazine such as reviews, previews, and/or interviews with community members.",
    "Maze": "Files containing content in which players navigate labyrinthine environments.",
    "Minigame": "Files containing one or more smaller games, with each often taking place on a single board.",
    "Mod": "Files containing content that modifies existing content.",
    "Multiplayer": "Files containing content intended for muliple players to participate together.",
    "Music": "Files which use audio as a major component of their design.",
    "Mystery": "Files which contain something to be solved or discovered over the course of the world",
    "Official": "Files containing content that is officially part of ZZT, having been submitted to Epic and published in an Epic released compilation of ZZT worlds. This consists of official releases of ZZT, Super ZZT, Best of ZZT, and ZZT's Revenge.",
    "Other": "Files that don't really do \"labels\".",
    "Parody": "Files that parody a shared cultural reference.",
    "Platformer": "Files that are played from a side-view usually with the player or player-controller object moving from side-to-side and jumping",
    "Puzzle": "Files that contain content focused on utilizing logical skills to find solutions.",
    "Racing": "Files that contain content requiring a player to get from Point A to Point B in a finite amount of time",
    "Random": "Files that play differently every time or files that are deliberately absurd in nature.",
    "Remake": "Files that remake existing games, either converting non-ZZT worlds to ZZT worlds or by enhancing existing ZZT worlds.",
    "Registered": "Files which were distributed to registered users.",
    "Retro": "Files which deliberately use the aethetics and design principles seen in older ZZT worlds.",
    "RPG": "Files that contain content with a focus on a character's story and character growth through new abilities/equipment. Typically uses some form of engine to provide turn based combat over ZZT's shooting mechanics.",
    "Sci-Fi": "Files that contain content which uses science fiction themes heavily.",
    "Shareware": "Files which requested some form of payment in order to receive a registered version. These files may sometimes have deliberately less content, or regular reminders to register not found in the registered version.",
    "Shooter": "Files that contain content focused primarilly on shooting, typically done via some sort of vehicle rather than having the player shoot directly.",
    "Simulation": "Files which contain content that attempts to simulate an activity.",
    "Space": "Files which contain content taking place in outer space.",
    "Sports": "Files which contain content based on sports.",
    "Story": "Files whose focus is on the story rather than the gameplay.",
    "Strategy": "Files that contain content in which the player oversees decisions that impact the results of a confrontation between rival factions.",
    "Toolkit": "Files which contain toolkits, one or more boards of elements in colors not normally accessible in ZZT's default editor. These have fallen out of use in favor of external editors that provide full access to all colors and elements ZZT supports.",
    "Trippy": "Files which contain content that tends to be surreal or dream-like. Does not inherently indicate drug use, but may.",
    "Trivia": "Files which contain content designed to quiz the player on one or more topics.",
    "Update": "Files which contain an updated release of a previously released file.",
    "Utility": "Files which contain tools to aid in creating ZZT worlds.",
    "WoZZT": "Files containing worlds created for \"Weekend of ZZT\" contests where entrants typically had 48 or 72 hours to create a ZZT game adhering to a given topic",
}

def main():

    for g in GENRES.keys():
        print(g)
        genre = Genre(title=g, description=GENRES[g])
        genre.save()
    return True


if __name__ == '__main__':
    main()
