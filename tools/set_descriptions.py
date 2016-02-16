#!/usr/bin/python
import os, sys, glob, zipfile, django
sys.path.append("/var/projects/z2")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()
from z2_site.models import *

INFO = {
    "7monday7.zip":"",
    "admd.zip":"",
    "anth.zip":"",
    "aura.zip":"A test of wits and speed, <i>Aura</i> is an instant classic of the modern ZZT scene.",
    "bananaq.zip":"It all started with a banana. A banana, and a man with a hand-held monkey. And, arguably, the greatest ZZT soundtrack _EVER_.",
    "bdisc1.zip":"",
    "BLDOATH.zip":"",
    "bluemoon.zip":"",
    "BOLETTE(FIX-A-DENT).zip":"Eat a mushroom? Bug out? Collect some purple keys? It must be a ZZT game! An odd and challenging adventure through a world filled with vibrant characters and technically impressive graphical effects.",
    "brandon1.zip":"Help Sir Alex of Brandonia save the eggs of the dragon from the evil Acro.",
    "buckver2.zip":"",
    "burgerj.zip":"Set in the 50's, you play Johnny, a teenager looking to make some quick cash. What better place to do it than in the very first fast food restaurant ever? Just look out for the freezer bears...",
    "burglar!.zip":"You are Luke Steel, an experienced burglar, thief, pickpocket, and all-around badass. Burgle like a pro while avoiding alarms, cops, and conspiracy!",
    "c-world.zip":"",
    "chknwire.zip":"",
    "compound.zip":"",
    "comxmas.zip":"",
    "corrupt.zip":"",
    "cwars11.zip":"",
    "cwars9.zip":"",
    "darksoul.zip":"",
    "death.zip":"A dark, atmospheric, and well designed shooter, _Death_ is sure keep your trigger finger happy up to the very end.",
    "defender.zip":"",
    "dizzy.zip":"",
    "dm-galry.zip":"Delve into darkness and pitch battle against fierce monsters and evil denizens to prove your worth as a hero.",
    "dracmon.zip":"",
    "dragoneye.zip":"",
    "driff.zip":"",
    "dwoods.zip":"Find a precious jewel and restore the rightful ruler in this classic Zenith Nadir game!",
    "elis_h_1.1.zip":"A competent blend of interesting puzzles, varied action, and captivating storytelling makes for a game no ZZTer should miss. A highly polished game worthy of emulation.",
    "endofwor.zip":"",
    "Esp.zip":"ESP is a massive four-file masterpiece that every ZZTer should play!",
    "ezanya.zip":"The dwarves have stolen royal artifacts from the palace. Delve into their underground hideaways and take them back.",
    "fabdemo.zip":"",
    "ffxtreme.zip":"",
    "foolqst.zip":"",
    "four.zip":"",
    "freedom.zip":"",
    "frost.zip":"Mmmmrrr...feeling really yiffy again. I had to paw-off so many times today it wasn't funny! I hate my icky human self. I want to be a real hermy little foxie, so I can be yiffed in my tailhole all day long..oooooh, mrrf.",
    "fury.zip":"",
    "ghunter.zip":"",
    "ghuntrse.zip":"",
    "kamek.zip":"",
    "knight.zip":"Join Ned in his quest to become a royal knight and save the kingdom from goobers and ruffians.",
    "kudzu21.zip":"Atmosphere is this game's specialty. Go forth and play Kudzu!",
    "lebensrm.zip":"Zenith Nadir's famous <i>Wolfenstein 3D</i> tribute, forerunner of several other ZZT action games.",
    "loap2.zip":"",
    "lome.zip":"",
    "lostmonk.zip":"",
    "lr9.zip":"",
    "lst.zip":"Far from our own reality, little square things strive to reach their only mission in their short life, to cover up the cyan fakes. Decide the fate of their race by guiding them to their goal.",
    "mbladep.zip":"",
    "megajob.zip":"",
    "merbotia.zip":"Who knew so much could be accomplished in a lifetime? Original humour still rules in this classic.",
    "merc.zip":"If you want a ZZT game that you can play over and over again, The Mercenary is the way to go!",
    "momentum.zip":"",
    "mooserulz.zip":"\"I - er - I'll do something mean to you!\"",
    "mout.zip":"",
    "neo1.zip":"",
    "new.zip":"",
    "nextgame.zip":"",
    "No.zip":"",
    "nothing.zip":"",
    "november.zip":"",
    "overflow.zip":"",
    "pheonix.zip":"",
    "pop.zip":"",
    "ppdv.zip":"",
    "quest-im.zip":"",
    "racerx.zip":"",
    "ripflesh.zip":"",
    "rp2000.zip":"",
    "run-on2.zip":"A random, chaotic adventure in a random, chaotic world. Delightfully evil fun!",
    "scooter.zip":"",
    "sivion.zip":"Djinnis, chthonic cults, and other sidequests abound in this classic Adventure RPG game!",
    "slimeline.ZIP":"",
    "Sombrero.zip":"",
    "syndrome.zip":"Want to make better ZZT games? This is a must-play, especially for first-time ZZT game makers.",
    "thief3.zip":"",
    "tp2.zip":"",
    "troope~1.zip":"",
    "v0mit.zip":"Freddy the ferret searches for the perfect drug.",
    "v2red.zip":"",
    "vo4.zip":"",
    "Voyage1.zip":"",
    "warlock.zip":"Pleana, a peaceful kingdom under a gentle ruler with three beautiful daughters. Nothing could possibly go wrong, right?",
    "wartorn.zip":"",
    "winter.zip":"School's rather boring to-day. Drift off into a lucid dream world and explore the depths of your subconscious.",
    "within19.zip":"",
    "wtemple.zip":"",
    "xod.zip":"",
    "yvs2.zip":"",
    "zemx.zip":"",
    "zztoxic.zip":"Help Smiley Guy thwart the antics of an evil mad scientist in these two classic ZZT adventures! (Spoiler: he gets laid at the end)",
    "zztris.zip":""
}

def main():
    for k in INFO.keys():
        try:
            file = File.objects.get(filename=k)
        except:
            print "NO SUCH FILE", k
            continue
            
        v = INFO[k]
        if v != "":
            file.description = v
            file.save()
            print "SAVED", k
    
if __name__ == "__main__" : main()