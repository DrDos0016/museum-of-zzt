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

SCROLL_BOTTOM = """\n │    •    •    •    •    •    •    •    •    •│
╞╧═════════════════════════════════════════════╧╡```"""
