# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import django, sys, os

sys.path.append("/var/projects/z2/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import *

titles = ["4", "Anthropoid", "Blood Oath", "Bloodlines Disc 1", "Blue Moon", "Buck Russel: Private Eye v2.0", "Burger Joint", "Burglar!", "ChickenWire v1.5", "Chrono Wars 11", "Chrono Wars 9", "Community X-Mas, A", "Compound", "Corrupt Mind", "Cyberworld", "Daemon Riff", "Dark Soul", "Death", "Defender of Castle Sin", "Draco Experience, The", "Dragon Eye", "Dwarvish-Mead Dream, A", "Edible Vomit", "End Of The World", "Escape/Planet Red v2.0", "Fabrication", "Fantasy World Dizzy", "Final Fantasy Extreme", "Fool's Quest, The", "Freedom", "Fury Spell", "Gem Hunter", "Gem Hunter SE 1.5", "Kamek", "Kudzu 2.1 (update, not sequel)", "Last Momentum", "Lebensraum", "Life of a Player 2", "Little Square Things", "LOME: The Legend of Matt Eatingham", "Long Voyage, The", "Los Refritos 9", "Lost Monkeys", "Merbotia", "Mercenary, The", "Mined Out", "Misandventures of Mega Job: The Epic Tag Team, The", "Mystic Blade", "Ned the Knight", "NEW Demo", "New Earth Operations Part 1", "NextGame 33", "NO!", "Nothing Constructive", "November Eve", "Overflow", "Pop ver.2", "PPDV", "Quest for the Immortals", "Rippled Flesh", "Run-On", "Rup Pig", "Scooter", "Sivion", "Slime Line", "Sombrero", "Speed Racer X", "Starship Troopers", "Teen Priest 2", "Thief 3", "Today Is Monday", "Voyage of Four", "Warlock Domain", "Warlord's Temple Beta", "Wartorn", "When East Met West: The Phoenix Reich", "Within v1.9", "xod", "You vs. Stupidity 2", "Zem! X", "ZZTris"]

fg_detail = Detail.objects.get(detail="Featured Game")

for title in titles:
    try:
        file = File.objects.get(title=title)
        file.details.add(fg_detail)
        print file.title + " is now featured!"
    except:
        print "FAIL FOR ", title