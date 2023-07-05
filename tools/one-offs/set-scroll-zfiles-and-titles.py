import os
import sys

import django

django.setup()

from museum_site.models import *  # noqa: E402

TITLES = [
    "Zero ain't used chief.",
    "Led Zeppelin lyrics",
    "This isn't a scroll",
    "Merbotian Poetry",
    "Get the MegaZeux version",
    "Weird sign, eh?",
    "Over 1000 exciting things to do",
    "You snag the hammer",
    "Lost rock creature",
    "But that's where the usual stopped",
    "It's tasty cuz it's blue!", # 10
    "Guinea Pig Fact",
    "The greater context of the feudal system",
    "Ping-pong-path Syndrome",
    "Why do these things always seem to happen to you?",
    "Nobody cleans this castle Man!!!",
    "Your name is MARY. You are a WITCH.",
    "Wet floor",
    "Xamboxumbadria is the powerhouse of the cell",
    "The chrono orb will be shattered!",
    "Obligatory rope", # 20
    "A more lucid daydream than usual",
    "You've been sucked!",
    "Lily had died.",
    "Would I lie to you?",
    "I REALLY HATE CHEATING SCUM",
    "Knock knock knock",
    "AKware members only",
    "Cheaters never prosper",
    "Winning over the crowd",
    "You feel you're going to need it", # 30
    "The Excommunication of Galileo",
    "How can I be sure you aren't lying?",
    "Skeleton face-off",
    "The fastest Kong in the west",
    "Fight, fight. Your country does call.",
    "ZOMBINATOR MANUAL VOL 1",
    "R&d... G#%en... Or*@$e...",
    "Mutations in city zoo!",
    "THE CHUTE",
    "The Venus D'Milo", # 40
    "Death comes for you, and his name is Basgard",
    "Question Lock",
    "What are you? Some kind of wimp?",
    "I'll rip your head off",
    "I'll kill you with a humongous chainsaw",
    "Courtesy of Nestle",
    "Women's lingerie store",
    "Nachos rule!",
    "My, what a handsom fellow!",
    "Greed has taken over the world.", # 50
    "Don't stumble over the lions.",
    "Dear trooper",
    "THIS IS J.P. FORMER LEAD SINGER FROM LED ZEPPLIN",
    "This is the escape hatch.",
    "Please use other door",
    "I AM THE HOSS",
    "Wow! She's really pretty!",
    "This pond is for everyone.",
    "Murderer and a looser",
    "Don't be a dick", # 60
    "Mean trick",
    "Kill everyone*",
    "Donkey Kong's Criminal Record",
    "Cloud castle chasm",
    "It'll have to do",
    "Dumb scrolls",
    "THE GOOD BEAR???",
    "We are still in love. Aren't we?",
    "What did the five fingers say to the face?",
    "Growf.", # 70
    "Contact lost with BooBoo",
    "What about life support?",
    "Bimbos",
    "Gaping Hole",
    "Welcome to Ikari Warriors",
    "VH1 vs. MTV",
    "The Mountain Porters",
    "I think I can live with that",
    "You saved the mayor, but...",
    "Don't shoot the geese", # 80
    "The legend of Skeletor",
    "One of your better works...",
    "LINK HEARS NOTHING BUT SILENCE",
    "It's to hard",
    "Daughter Brain",
    "WELCOME TO PICKLE LAND!",
    "Save Mary Jo Lee",
    "Poor security",
    "Just sit back and relax",
    "WHAT DO YOU THINK IS MOST IMPORTANT IN LIFE?", # 90
    "Kill the ruffian king",
    "YOU ARE THE ONE AND ONLY WEIRDO",
    "Hi! Welcome to Destroy Barney Three",
    "WHEN I MESSED UP, I WAS MESSED UP",
    "OH NO!! I HATE BARNEY!",
    "Get moving, butt-hole",
    "Danger! Red Dragon",
    "That's life",
    "A teller will be with you in a second",
    "Horse", # 100
    "Shame on you",
    "Rat's eyeball",
    "We are trapped in here forever.",
    "please don't shoot me",
    "Just what I've always wanted",
    "Meet Espio",
    "The death of Matt Derek",
    "You shouldn't go through other people's closets...",
    "I have rated the girls I dated.",
    "You switch on the TV", # 110
    "You've got me!",
    "If you die...",
    "You won't need the fishing rod anymore",
    "This library is infested with Ruffians",
    "The power of ZZT is strong",
    "Anyone can curse if they want to",
    "Shade diagonally",
    "You'd better save now",
    "The ultimate bait",
    "Driven insane by the electrical storm", # 120
    "Think before you take off!",
    "Can you conquer all seven levels yet?",
    "You think I believe that kinda' shit?",
    "The harmless, innocent sign",
    "486DX 33 MHz",
    "She always was weird.",
    "Do you know how to engage in a swordfight?",
    "Have any advice?",
    "This here is the torture room",
    "Give me some points.", # 130
    "Compact ammo",
    "Trap wire",
    "Damn it!",
    "Uninhabitable planet",
    "If you were a human",
    "Invisible wall",
    "Testing the Skull Men",
    "Your part of the Royal Navy?!",
    "Well done, worthy one.",
    "That guy in the village must of lied", # 140
    "Nya Nya's",
    "Great feeling",
    "No swimming",
    "rip to my husband",
    "Snakes, demons, and ghosts",
    "WHO DARES ENTER",
    "NO ONE BUYS HOT DOGS FROM ME",
    "IF YOU ARE READING THIS",
    "In Fond Memory of #darkdigital",
    "How'd you get out of jail?", # 150
    "Oh, no!",
    "DON'T take the energizer",
    "WANTED",
    "You have saved my wife",
    "Char Char!",
    "Hello Pikachu...",
    "Autograph magic",
    "Meet our game show host",
    "Why, I ought to take revenge!",
    "Surgeon general's warning", # 160
    "Parents!",
    "Star War(s) ZZT",
    "The point of this games",
    "HHHHHHEEEEEELLLLLPPPP ME PLEASE",
    "Special asinment",
    "Sea shanties are forbidden",
    "A Popular Spot",
    "I do not ENJOY stealing.",
    "Look, you can see my wife!",
    "Welcome to First Florian Church", # 170
    "Get off!",
    "Who says you can come here?",
    "You die now Chief!",
    "BAD ENDING",
    "Why this happens, we do not know",
    "Can you give any advice?",
    "Discussing the American Civil War",
    "This is not the door!",
    "The water cannot cleanse you of your sins.",
    "A Guide to Herbs", # 180
    "If you kill for no reason",
    "BIKE STOLEN!",
    "Come back when you understand what I mean.",
    "Another Gaping Hole",
    "It just sits there, waiting.",
    "Halfing",
    "You should never tell anybody that you're from the past.",
    "First Car Simulation Ever!",
    "You found a Black key!",
    "I don't know much about art", # 190
    "Eerie dialtone",
    "Oil begins to leak out into the water.",
    "Thinking logically",
    "Yet Another Gaping Hole",
    "Purple tree",
    "Fascinating...",
    "Please be careful",
    "I was arrested",
    "Give me your money or your life",
    "LEVEL UP!", # 200
    "You got the Mermish Triton!",
    "Just... imagination....",
    "Damn those NASA analysts",
    "People have died on this road",
    "How corny!",
    "The blood tube",
    "I'm sorry I can't help you.",
    "Remember",
    "Warehouse Manifest",
    "The ZZT engine sure is powerful.", # 210
    "It's hardly even a puzzle any more",
    "Significant work experience",
    "What are you talking about, Lance?",
    "Hello",
    "We should be able to revive Lenin in a matter of hours.",
    "I'm here looking for cute guys",
    "Stay away from my gold!",
    "I have taken your Krabby-Patties to Mt. Toilet!",
    "Micochip Schematic",
    "The way of ZZT", # 220
    "Here is a toothpick",
    "This is the Checkerboard Center",
    "A good glass of milk",
    "Techno-yeehaw!",
    "Here's your medium 7-Up",
    "A viscerally exciting experience",
    "Be proud.",
    "You can do better than that.",
    "The best resturant in town",
    "I will not give you the gun...", # 230
    "I hate when this happens.",
    "Building over nature",
    "It's only a girl!",
    "I'll survive... but you?",
    "I-am-Omega.",
    "Let's play name the body part!!",
    "Employees Must Wash Hands",
    "You have now attained the high rank of",
    "Lion Alert",
    "A Wise Saying", # 240,
    "Think about this very carefully",
    "DIE, CHEATING SCUM-OF-THE-EARTH!!!",
    "Checkered floor",
    "I hope you made friends",
    "Welcome to the City of ZZT",
    "Annoying",
    "Blank",
    "The Shimmering Jewel-Incrusted Crown",
    "Notice to All Who Would see the King",
    "Now I'll never learn", # 250
    "Come, if you must, to the ruler you crowned",
    "You pick up your phaser rifle.",
    "I am the special slider.",
    "ID number?",
    "He bopped Biff!",
    "You now have the black key.",
    "So close yet so far",
    "Oops",
    "Ignorant on the usbject of death",
    "Blessed sticks", # 260
    "Alright monkey boy!",
    "BAZAAR",
    "Beautiful torches",
    "By the way",
    "Rook Eldain has arrived",
    "You need to get MegaZeux",
    "So, what did you THINK of it?",
    "Please order to get full version",
    "I needed that",
    "WELCOME TO LYSANDER THE GREAT'S CALVIN AND HOBBES GAME", # 270
    "Useful Information",
    "This game is harder than the last",
    "Dumb tigers",
    "Get out of here, QUICKLY!",
    "A rather nice looking vase",
    "He always has a large grin",
    "Cast of characters",
    "Flagg's Creatures",
    "It's my worst enimies!",
    "Nobody plays marbles anymore", # 280
    "You plug your laptop into a nearby plug.",
    "The chicken is worth 3 points",
    "That's one unusual pizza!",
    "You step on a seemingly solid ground",
    "Swords are for vanqueshing",
    "If you thought this was tough",
    "Thou art not worthy!",
    "You win!",
    "The passage will be destroyed.",
    "HERE LIES THOR HAMMERHAND", # 290
    "Scroll of Friends",
    "Scroll of Fart",
    "Scroll of Spikey-Hair",
    "Scroll of Health",
    "Scroll of Smartness",
    "You have found a way to my castle.",
    "I am ZZT.",
    "Don't dispair.",
    "May I take your harmonica?",
    "Hold on.", # 300
    "DUPLICATE OF 150",
    "Forget your quest!",
    "The Inn Rooms",
    "This bank is for the rich only!",
    "Speaks for itself",
    "Here take this gun",
    "How to kill a vampire",
    "Cris Cornell",
    "I'll show you crack",
    "THE ROOM OF EXTREAM ANNOYANCE AND FRUSTRATION!", # 310
    "You have strayed from the path",
    "Gurgi is sorry.",
    "What is a human?",
    "Here's yer crossbow.",
    "You can get away with a lot more stuff",
]


def main():
    qs = Scroll.objects.all().order_by("id")

    idx = 1
    for s in qs:
        print(s.title)
        if s.zfile_id is None:
            if s.pk >= 113:
                src = s.source.replace("/file/view/", "")
                key = src.split("/", 0)[0].split("/")[0]
            else:
                src = s.source[8:].split("/")[0]
                key = src.split("?")[0]

            key = key.replace("%20", " ")
            print(s.id, key)

            zf = File.objects.get(key=key)
            s.zfile = zf

        s.title = TITLES[idx]
        s.save()
        idx += 1
    return True


if __name__ == '__main__':
    main()
