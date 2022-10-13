import os

if os.path.isfile("/var/projects/DEV"):
    WOZZT_URL = "http://django.pi:8000/api/worlds-of-zzt/?category=discord"
else:
    WOZZT_URL = "https://museumofzzt.com/api/worlds-of-zzt/?category=discord"

COOLDOWN_MESSAGE = "`!{}` is on cooldown for {} more second(s)."

HELP = """```
List of commands:
  !addrole     Add one or more roles.
  !help        Shows this message.
  !removerole  Remove a role.
  !scroll      Some reading material. (10 sec. cooldown)
  !zzt         Shows a random ZZT board. (15 sec. cooldown)

List of roles:
  ZZTer       MZXer
  He/Him      She/Her     They/Them
  Stream-Alerts-All       Stream-Alerts-Asie
  Stream-Alerts-Dos       Stream-Alerts-Meap

All commands are restricted to the #bots channel, excluding !zzt which also functions in #worlds-of-zzt-feed.
```"""

SCROLL_TOP = """```
╞╤═════════════════════════════════════════════╤╡
 │                  Scroll ##                  │
 ╞═════════════════════════════════════════════╡
 │    •    •    •    •    •    •    •    •    •│"""

SCROLL_BOTTOM ="""\n │    •    •    •    •    •    •    •    •    •│
╞╧═════════════════════════════════════════════╧╡```"""

SCROLLS = [
{
"text":'''"It is whispered that soon
 if we all call the tune,
 then the piper will lead us to reason.

"And a new day will dawn
 for those who stand long
 and the forests will echo with laughter."

                   -Led Zeppelin''',
"source":"https://museumofzzt.com/file/z/zzt.zip?file=TOWN.ZZT&board=2#21,9"},

{
"text":"This isn't a scroll, it's a flashing PHI.",
"source":"https://museumofzzt.com/file/z/zzt.zip?file=DUNGEONS.ZZT&board=18#29,5"
},

{
"text":"""Creatures of Merbotia , Unite!
With skin both Red, and Blue and White.
Kill this man who thinks it's right
To avoid this display of Power and Might!

Make him die, just like the few
Which challenged the power of me, and you.
Gobble him up like Chunky beef stew.
Or else you'll make me blue!

$Uh oh, I sense an action scene...""",
"source":"https://museumofzzt.com/file/m/merbotia.zip?file=MERBOTIA.ZZT&board=14#54,11"
},

{
"text":"""But this isn't what happens in the MZX
version!""",
"source":"https://museumofzzt.com/file/s/sivion.zip?file=SIVION.ZZT&board=75#9,19"
},

{
"text":"""$Sign says:

    New entering downtown ZZT.  Watch out
for muggers and STAY AWAY from the
infamous Dr. Bob!

$Weird sign, eh?""",
"source":"https://museumofzzt.com/file/z/zzt.zip?file=CITY.ZZT&board=10#8,22"
},

{
"text":'''$The Mayor speaks:

    "Welcome to the City of ZZT, my fellow
citizen.  This is the town of over 1000
exciting things to do, including the
world's largest ball of string,  the
ZZT senior citizens rap choir and many
other exciting tourist attractions..."''',
"source":"https://museumofzzt.com/file/z/zzt.zip?file=CITY.ZZT&board=18#53,22"
},

{
"text":"""you snag the hammer and place it in your
FURR""",
"source":"https://museumofzzt.com/file/e/v0mit.zip?file=VOMIT.ZZT&board=12#4,24"
},

{
"text":"""$Hello! My name is _STUMPY_
$I belong to _HENNA SULLRUNE_
$I live at _THE ONE HOUSE IN THE HAUNTED
$SWAMP IN VASQUETH FOREST, YOU CAN'T MISS
$IT AND IT'S NOT LIKE THIS PLACE IS
$OVERPOPULATED OR ANYTHING_""",
"source":"https://museumofzzt.com/file/f/frost1.zip?file=FROST1.ZZT&board=19#35,14"
},

{
"text":"""You went to sleep tonight as usual.

You dressed for bed as usual.
You pulled back the covers as usual.
You turned out the light as usual.

But that's where the usual stopped.


Just as you were drifting off to sleep,
you heard an eerie voice drift through
your head...

$Hello, mortal.
$I am the Sandman.
$And you are my prisoner.""",
"source":"https://museumofzzt.com/file/n/nmzzt.zip?file=NGHTMARE.ZZT&board=1#1,1"
},

{
"text":"""wow! it's a bottle of Blue When Brand
Sauce!

$shapiro & triangy!
yum! it's tasty cuz it's blue!""",
"source":"https://museumofzzt.com/file/m/shaplies.zip?file=SHAPLIES.ZZT&board=7#32,4"
},

{
"text":"""$You have passed level 12!
Guinea Pig Fact ──·
$Guinea Pigs are considered to be social
$animals and do well in pairs.""",
"source":"https://museumofzzt.com/file/s/scooter.zip?file=SCOOTER.ZZT&board=15#55,11"
},

{
"text":"""The King turns livid as you approach
his costly garb, and speaks:

"How dare you touch me, impudent Peasant!
I shall teach you to kneel in my
presence! Guards!"

As the guards haul you away, you reflect
on the merits of big city life in the
greater context of the fuedal system
which has brought you to this sorry end.""",
"source":"https://museumofzzt.com/file/e/Ezanya.zip?file=EZANYA.ZZT&board=1#50,10"
},

{
"text":"""$This one is just nasty.

Ping-pong-path Syndrome is one of the few
Syndromes that becomes a Syndrome with
only one incident.  It is the ONLY Fatal
Syndrome that is fatal to the adventure
for a reason other than making the game
nearly impossible (aside from the somewhat
rare TryMe Trap and the utterly ridiculous
Gimme-money Syndrome).""",
"source":"https://museumofzzt.com/file/z/syndrome.zip?file=SYNDROME.ZZT&board=7#52,15"
},

{
"text":'''"Hey! Where is my picture!?!?!?!"
$He looks at you and glares...
"You wouldn't know anything about this,
would you?" he growls.
$You gulp and mutter,
"Is that mother calling me? I better go."

$He stops you.
"Not so fast, young man."
$Uh oh, I better go. This doesn't look too
$good for you, Joshua. Why do these things
$always seem to happen to you?''',
"source":"https://museumofzzt.com/file/c/cliff15.zip?file=CLIFF15.ZZT&board=1#48,12"
},

{
"text":"""Nobody cleans this castle Man!!!""",
"source":"https://museumofzzt.com/file/a/aceland.zip?file=ACELAND.ZZT&board=28#46,7"
},

{
"text":"""Your name is MARY. You are a WITCH, and
today is a very important day for you.

Today, you're sacrificing your very first
PRINCESS!

Around these parts, every witch worth her
weight in bat guano has sacrificed at
-least- one princess. After all, the only
way to obtain DARK MAGIC POWER is to make
ritual sacrifices to the DARK EMPRESS.

And everyone knows princesses are the most
powerful sacrifice of all!""",
"source":"https://museumofzzt.com/file/a/atwt.zip?file=WITCHTWR.ZZT&board=6#26,13"
},

{
"text":"""This is the sparkling clean toilet that
your mom doesn't let anyone use.
That's why the floor in here is so wet.""",
"source":"https://museumofzzt.com/file/f/fred1gld.zip?file=FRED1GLD.ZZT&board=4#34,21"
},

{
"text":'''"xamboxumbadria".

an organism which lives within all
hoodians, the xamboxumbadria is a more
powerful form of mitochondria, and it
helps hoodians live about forty-two months
longer than humans. it does not exist
within earth humans.

what if the xambozumbadria had minds of
their own?

what if they were to awaken and take over
the universe?
''',
"source":"https://museumofzzt.com/file/n/november.zip?file=NE-A.ZZT&board=3#27,12"
},

{
"text":"""glenn: bestial!

bestial: what!? how did you find me?
i guess you are smarter than i thought..

glenn: stop this at once! if you destroy
forepast, the chrono orb will be
shattered! we will be trapped here!

bestial: well then. this is your chance
to battle me dwarf! come on! (passage)""",
"source":"https://museumofzzt.com/file/d/admd.zip?file=ADMD.ZZT&board=56#56,11"
},

{
"text":"""KIM: Ooh. The obligitory rope. Classic ZZT
item.""",
"source":"https://museumofzzt.com/file/n/november.zip?file=NE-B.ZZT&board=22#12,6"
},

{
"text":"""as you exit the palace, you decide that
this has been a more lucid daydream than
usual. you tell yourself that it's just a
string of random thoughts and patterns but
still you can't help but feel that someone
else might be in control. and as you face
the distant peaks, you're not sure if you
want to leave.""",
"source":"https://museumofzzt.com/file/w/winter.zip?file=winter.zzt&board=43"
},

{
"text":"""Argh!  You've been sucked!""",
"source":"https://museumofzzt.com/file/z/zzt.zip?file=CAVES.ZZT&board=35#28,10"
},

{
"text":"""Lily had died.
$
$And like a boat out on the ocean
$I'm rocking you to sleep
$The water's dark
$And deep inside this ancient heart
$You'll always be a part of me
$                   - Billy Joel, Lullabye""",
"source":"https://museumofzzt.com/file/c/compound.zip?file=COMPOUND.ZZT&board=19#26,13"
},

{
"text":"""Man-Hey you your not supposed to be here.
$Yes I am I'm the inspector.
Man-Really?
$Of course would I lie to you.
Man-yes you might.
$well just don't attack me.
Man-and just don't hurt me""",
"source":"https://museumofzzt.com/file/s/sac.zip?file=S.A.C..zzt&board=16#45,6"
},

{
"text":"""Hey! You've obviously not played any of my
previous games; if you did, you would know
by now that I REALLY, REALLY HATE CHEATING
SCUM LIKE YOU!!!!!!!! By the way, you're
dead.""",
"source":"https://museumofzzt.com/file/d/dwoods.zip?file=DWOODS.ZZT&board=25#1,25"
},

{
"text":"""You: (Knock knock knock)

Genhis Kahn: ÖÖG.""",
"source":"https://museumofzzt.com/file/b/bananaq.zip?file=BQUEST.ZZT&board=14#24,14"
},

{
"text":"""'This is a trademark of AKware, and so
'is the muzak. Therefore, if you use it
'in the game, and you are not in AKware,
'then we will find out somehow and you
'will pay.""",
"source":"https://museumofzzt.com/file/a/akmag7.zip?file=akmag7.zzt&board=8#7,23"
},

{
"text":"""Dear player-

      If you are reading this, you are
cheating! And, as always, cheaters never
prosper.
                        Sincerely,
                        AKNeutron""",
"source":"https://museumofzzt.com/file/y/yvs2.zip?file=YVS2.ZZT&board=39#45,5"
},

{
"text":"""Nyarlethole:

Ahem. A vote for the ESP is a vote for
chaos, bloodshed, and human suffering.

(Wild cheers erupt from the crowd. The
debate is clearly over.)""",
"source":"https://museumofzzt.com/file/e/Esp.zip?file=ESPFILE1.ZZT&board=15#2,17"
},

{
"text":"""You get your rifle and 20 rounds of ammo.
Somehow, you feel you're going to need it.""",
"source":"https://museumofzzt.com/file/c/codered.zip?file=CODERED1.ZZT&board=1#55,4"
},

{
"text":"""Yes, I was excommunicated for discovering
that earth was not in fact the center of
the universe. This was against their
beliefs, so they made me leave their
church even though I had solid proof
that earth actually orbits the sun.""",
"source":"https://museumofzzt.com/file/m/project.zip?file=PROJECT.ZZT&board=19#30,14"
},

{
"text":"""KING:  How can I be sure you're aren't
lying?

ALEX:  I can't lie, remeber?!

KING:  Oh, yeah.  What were you saying
about those dragon eggs?

ALEX:  Acro trancefered the other eggs
to a parallel dimension.

KING:  Acro!  Get him!""",
"source":"https://museumofzzt.com/file/l/brandon1.zip?file=BRANDON1.ZZT&board=6#15,8"
},

{
"text":"""You find yourself faced with a skeleton.
He carries a sword and disappears now and
then. He screams and attacks you.""",
"source":"https://museumofzzt.com/file/j/jack-o-l.zip?file=Jack-o-l.zzt&board=10#36,17"
},

{
"text":"""I am Sonic Kong Jr.
I am the fastest Kong in the West.....

....Not to mention East North and South.
Te, He.""",
"source":"https://museumofzzt.com/file/l/linkadv1.zip?file=LINKSADV.ZZT&board=60#30,8"
},

{
"text":"""all:fight, fight.  your country does call.

soldier:i'd fight for nothing at all!

all:the drums, the hate, the deadly sound

soldier:can you hear your own heart pound?

soldier:can you see the en'my downed?""",
"source":"https://museumofzzt.com/file/f/freedom.zip?file=freedom.zzt&board=36#4,25"
},

{
"text":"""ZOMBINATOR MANUAL VOL 1
            Mission Statement
             by Zombinator I

Zombies are mindless creatures attracted
to human life forms. Zombies are extremely
dangerous. If a zombie touches you, you
will die instantly!
""",
"source":"https://museumofzzt.com/file/z/ZOMBINAT.ZIP?file=ZOMBINAT.ZZT&board=1#10,2"
},

{
"text":"""Zzz.t... Zz..t.t... R&d...
G#%en... Or*@$e...

You think it has something to do with
his IO interface. You carefully open it
up and see a tangle of wires...

Which one will you move?""",
"source":"https://museumofzzt.com/file/r/robot.zip?file=ROBOT.ZZT&board=8#19,7"
},

{
"text":"""The printout reads:

$Mutations in city zoo!

   Toxic waste is the beleived creator of
the many strange mutations at the city
zoo, says the head zookeeper.  They are
highly poisonous and many are almost
invincible.  Weapons are kept on hand that
CAN destroy any of them, so no one should
be worried.

                Taken from The Daily Moon,
                              July 4, 1992""",
"source":"https://museumofzzt.com/file/c/codered.zip?file=CODERED1.ZZT&board=1#34,3"
},

{
"text":"""But I'm going to tell it how it is,
folks: there is NO WAY Yuki gets past
this. THE CHUTE is the most brutal
challenge ever created. It has more
traps, requires more speed, and demands
more skill than ANYTHING arena-makers
have EVER created...

$░▒▓█Save Your Game█▓▒░""",
"source":"https://museumofzzt.com/file/y/Yuki.zip?file=Yuki.zzt&board=39#31,3"
},

{
"text":"""    OOOHHHHHH.... The Venus D'Milo, eh?
*WINK* *WINK* Whatever are the chances
are it showing up directly after I sold a
magic hammer? *NUDGE* *NUDGE* Say no
more... here's $12000 for it. A fair price
for this ORIGINAL.""",
"source":"https://museumofzzt.com/file/s/ARCH.zip?file=ARCH.zzt&board=3#20,8"
},

{
"text":'''$"GENTLEMEN!"
I exclaimed, instantly gathering
everyone's attention, as I was the only
member of the Raven Watch in the tavern.

$"I have an announcement to make. You're
$all dead, all corpses, all of you. Every
$last one. Enjoy your beers, death comes
$for you, and his name is Basgard."''',
"source":"https://museumofzzt.com/file/r/rvnfall11.zip?file=rvnfall.zzt&board=7#30,14"
},

{
"text":"""You have tried to unlock a Question Lock.
It would be wise to push ENTER and Save
your game before you touch this again.
Ok,You get one try.(you should've shot all
the enemies)If you get the Question Right,
you will gain passage to the grove.If you
don't,The lock will turn into a Wall.
Here's the question:

How do you say "Good Night" in Spanish?""",
"source":"https://museumofzzt.com/file/s/SONIC.zip?file=SONIC.ZZT&board=29#55,3"
},

{
"text":"""A Coke? What are you? Some kind of wimp?
Let's get 'im, boys!""",
"source":"https://museumofzzt.com/file/f/fquest15.zip?file=FQUEST15.ZZT&board=6#50,22"
},

{
"text":"""|---------------|
|-={[Warning]}=-|
|---------------|
       ||
       ||
       ||
_______||______________________________

If you use this I'll rip your head off
and use it for a balling ball.
_______________________________________""",
"source":"https://museumofzzt.com/file/t/Test.zip?file=TEST.ZZT&board=8#31,3"
},

{
"text":"""This room is made by Nadir for this game
$ONLY
If you copy this board into one of your
games, I will track you down and kill you
with a humongous chainsaw. Thank you.

This scroll is (c) by Crazy Panda in 2002
""",
"source":"https://museumofzzt.com/file/s/magicflamingo.zip?file=MagFlam.ZZT&board=31#33,3"
},

{
"text":"""I'm sorry Red, but you were too slow.
But we do have these great fifty dollar
savings bonds for you courtesy of Nestle.

$ _______________________________________
$|50|             NESTLE              |50|
$|~~              _______              ~~|
$|               /       \               |
$|       H      |  O   O  |      8       |
$|\             |    >    |             /|
$|50\           |   \_/   |           /50|
$|____\__________\_______/__________/____|""",
"source":"https://museumofzzt.com/file/l/legends.zip?file=LEGENDS.ZZT&board=1#7,24"
},

{
"text":"""You didn't really think I'd program in
a women's lingerie store did you???!!!!!
You should be ashamed to have tried to
come in here in the first place!
Geez....
$           -the programmer""",
"source":"https://museumofzzt.com/file/s/ancient.zip?file=ANCIENT2.ZZT&board=64#31,13"
},

{
"text":"""It's the food conjurer.

Charlie-I want some nachos!

$...BEEP! BEEP!...

Charlie-Nachos rule!""",
"source":"https://museumofzzt.com/file/o/overflow.zip?file=OVERFLOW.ZZT&board=41#45,13"
},

{
"text":"""You punch him in the face and his head
bangs into his friend's head.  His friend
plumetts into the water where he is
devoured by sharks.  The soldier lays on
the ground dead.  You figure that
the only way to get around here is to have
a British uniform.  You take his uniform
and put it on.  My, what a handsom fellow!""",
"source":"https://museumofzzt.com/file/t/timewii.zip?file=timewii.zzt&board=20#2,5"
},

{
"text":"""$Greed has taken over the World. Mobs
$are creating 98% percent of deaths
$each year just for money.""",
"source":"https://museumofzzt.com/file/u/U-A.zip?file=UA.zzt&board=7#2,22,1"
},

{
"text":"""This room contains explicit,
        adult, graphic, material.
  Please enter only if you are over 21!
     (Don't stumble over the Lions.)""",
"source":"https://museumofzzt.com/file/d/Darby.zip?file=DARBYTWN.ZZT&board=3#49,16"
},

{
"text":"""Dear trooper
well....
if your reading this..
then you must have lived...
and I must be dead...
we just can't have that..
can we???

love,
Ma alien

p.s...

you lose...""",
"source":"https://museumofzzt.com/file/a/alien.zip?file=ALIEN.ZZT&board=14#47,15"
},

{
"text":"""HEY MAN THIS IS J.P. FORMER LEAD SINGER
FROM LED ZEPPLIN. TAKE THE AMMO AND GEMS
AND FIND OUT WHO IS THE GUY THAT IS TRYING
TO KILL ALL THE ROCK STARS.  HURRY!""",
"source":"https://museumofzzt.com/file/a/ArcadeBBSRemainder.zip?file=ROCKLAND.ZZT&board=1#55,15"
},

{
"text":"""$\"This is the escape hatch, I use it
$when ever I am in deep shit.\"""",
"source":"https://museumofzzt.com/file/b/baloo.zip?file=BALOO.ZZT&board=40#16,13"
},

{
"text":"""$\"The door says: Please use other door,
$lives have been lost.\"""",
"source":"https://museumofzzt.com/file/b/baloo.zip?file=BALOO.ZZT&board=48#17,7"
},

{
"text":"""$
DIZZY: OHH DEAR THE HOSS IS HEEEEERE
DRAGON: I AM THE HOSS
$""",
"source":"https://museumofzzt.com/file/f/dizzy.zip?file=DIZZY.ZZT&board=22#44,6"
},

{
"text":"""An attractive picture of Drew Barrymore.
Wow! She's really pretty!""",
"source":"https://museumofzzt.com/file/i/invasionzztr.zip?file=INVZZTRV.ZZT&board=19#39,7"
},

{
"text":"""This pond is for everyone. Don't pollute.

Many people have left stuff in the lake.
If you find anything let us know...

Pond caretakers
1 - (555) 555 - 5555

LOST:
1. Watch
2. Glitter gewlery
3. Pokémon squirtle gun""",
"source":"https://museumofzzt.com/file/i/invasionzztr.zip?file=INVZZTRV.ZZT&board=38#21,19"
},

{
"text":"""There is a reason I won.
I was in control of myself even in the
heat of battle.

When the anger is in control only blind
fury exists. Intelligence is the key to
everything, and you lost yours while I
kept mine.

Now you are a murderer and a looser.""",
"source":"https://museumofzzt.com/file/i/invasionzztr.zip?file=INVZZTRV.ZZT&board=51#39,14"
},

{
"text":"""$Don't be a dick:

    If this game goes into basic,  please
type RUN at the \"]\" prompt.""",
"source":"https://museumofzzt.com/file/f/FLIMTOWN.zip?file=FLIMTOWN.zzt&board=12#30,20"
},

{
"text":"""This puzzle has a mean trick in it.""",
"source":"https://museumofzzt.com/file/r/RRPUZZLE.zip?file=RRPUZZLE.ZZT&board=1#23,18"
},

{
"text":"""Gandalf forewarned me of your arrival here
in Bree.

Listen, to get out, you must kill everyone
in Bree (except me) and talk to the Yellow
Man, who will let you open the gate."

\"Good luck!\"""",
"source":"https://museumofzzt.com/file/m/midearth.zip?file=MIDLERTH.ZZT&board=25#37,7,8"
},

{
"text":"""Prisoner No. 7
Donkey Kong
Wanted for stealing bananas and making a
jerk of himself.""",
"source":"https://museumofzzt.com/file/y/yoshiadv.zip?file=YOSHIADV.ZZT&board=21#38,6"
},

{
"text":"""Alternatively, I'll bet you're wondering
how there is a 500 foot chasm in a cloud
castle. WELL I'M NOT TELLING YOU YOU DEAD
PERSON""",
"source":"https://museumofzzt.com/file/z/dizzyzzt.zip?file=DIZZY.ZZT&board=38#16,18,1"
},

{
"text":"""$
$\"Eeew! A dead bear in a pool of blood!\"
$
JOE:\"It'll have to do.\"
$""",
"source":"https://museumofzzt.com/file/c/Cwars.zip?file=CWARS5.ZZT&board=11#36,6"
},

{
"text":"""Don't you hate having to read all these
dumb scrolls?""",
"source":"https://museumofzzt.com/file/c/COOLZAP.ZIP?file=COOLZAP1.ZZT&board=3#18,2"
},

{
"text":"""REMEMBER THIS SPECIAL BEAR??
THE GOOD BEAR???""",
"source":"https://museumofzzt.com/file/c/TIPS.ZIP?file=TIPS.ZZT&board=1#48,8"
},

{
"text":"""Addison just asked if we're still in love.

          Oh Jesus. That girl.

Yeah, but, we are still in love.

Aren't we?

          Let's talk about it when I get
          home.""",
"source":"https://museumofzzt.com/file/a/ana.zip?file=ANA.ZZT&board=20#23,18"
},

{
"text":"""YOU: What did the five fingers say to the
face?

KEY CUTTER: (uncomprehending) ...what???""",
"source":"https://museumofzzt.com/file/l/TROLLOL.zip?file=TROLLOL.ZZT&board=4#47,9"
},

{
"text":"""  Growf. I give up. Here,take my wealth.""",
"source":"https://museumofzzt.com/file/l/landxfix.zip?file=LAND2FIX.ZZT&board=18#42,2"
},

{
"text":"""Com # 7rQ-eosProt
Re: Penitentiary LOC

Proteus recently lost contact with the
penal colony on Bo-BOO35 ("BooBoo").
It is believed that a prisoner revolt may
be responsible for the loss of contact.
Investigate Bo-BOO35 and gather data.
Then go on to your next mission (see other
message rod).
""",
"source":"https://museumofzzt.com/file/l/land.zip?file=LANDV20.ZZT&board=2#36,19"
},

{
"text":"""$
JANE: But what about the systems governing
      life support?
$

$
HUDSON: Oh, yeah. I'll protect the life
        support program. <click, click>
$""",
"source":"https://museumofzzt.com/file/c/cwars9.zip?file=CWARS9.ZZT&board=22#30,21"
},

{
"text":"""$
GUARD: Something's wrong with the computer
       on this level of the tower. Does
       this have something to do with YOU
       bimbos?!?!
$""",
"source":"https://museumofzzt.com/file/c/cwars9.zip?file=CWARS9.ZZT&board=25#39,14"
},

{
"text":"""$
$Big Gaping Hole
$
  A viewing hole to look through the
viewing hole below!
$""",
"source":"https://museumofzzt.com/file/c/cwars9.zip?file=CWARS9.ZZT&board=45#12,10"
},

{
"text":"""Ah, welcome to Ikari Warriors. Control one
of two (really just one) overweight, head
band wearing, Rambo wannabes. Invaded by
an evil communist foriegn power, Ikari is
a young nation, ruled by Shinji, a nerdy
14 year old Japanese kid. This is SKC
Soft's first game, so there might be a
few bugs. Good Luck!""",
"source":"https://museumofzzt.com/file/i/Ikari.zip?file=Ikari.zzt&board=2#3,22"
},

{
"text":"""$November-6, 15th, 1997
Stopped watching MTV. And started to watch
VH1. VH1 simply kicks MTV's ass.""",
"source":"http://museumofzzt.com/file/g/ghanth.zip?file=Ghrpg.zzt&board=5#37,16"
},

{
"text":""" These are the Mountain Porters. If you
get aggrivated easily then this board was
madee specially for you. But if you are
the patient type then this screen just
wasted me half an hour.""",
"source":"https://museumofzzt.com/file/l/LCROWN_3.ZIP?file=LCROWN-3.ZZT&board=26#4,15"
},
]
