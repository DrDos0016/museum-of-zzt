ELEMENT_NAMES = ["ammo", "bear", "blinkew", "blinkns", "blinkwall", "bluetext", "bomb", "boulder", "breakable", "bullet", "customtext", "cyantext", "darkness", "door", "duplicator", "edge", "empty", "energizer", "fake", "forest", "gem", "greentext", "head", "invisible", "key", "lion", "monitor", "normal", "passage", "player", "purpletext", "pusher", "redtext", "ricochet", "ruffian", "scroll", "segment", "shark", "sliderew", "sliderns", "slime", "solid", "spinninggun", "star", "tiger", "torch", "transporter", "water", "whitetext", "yellowtext", ]

COLORS = ["black", "dkblue", "dkgreen", "dkcyan", "dkred", "dkpurple", "brown", "gray", "dkgray", "blue", "green", "cyan", "red", "purple", "yellow", "white"]

ELEMENT_IDS = {
"ammo": 5, "bear": 34, "blinkew": 33, "blinkns": 43, "blinkwall": 29, "bluetext": 47, "bomb": 13, "boulder": 24, "breakable": 23, "bullet": 18, "customtext": 0, "cyantext": 49, "darkness": 0, "door": 9, "duplicator": 12, "edge": 1, "empty": 0, "energizer": 14, "fake": 27, "forest": 20, "gem": 7, "greentext": 48, "head": 44, "invisible": 28, "key": 8, "lion": 41, "monitor": 3, "normal": 22, "passage": 11, "player": 4, "purpletext": 51, "pusher": 40, "redtext": 50, "ricochet": 32, "ruffian": 35, "scroll": 10, "segment": 45, "shark": 38, "sliderew": 26, "sliderns": 25, "slime": 37, "solid": 21, "spinninggun": 39, "star": 15, "tiger": 42, "torch": 6, "transporter": 30, "water": 19, "whitetext": 53, "yellowtext": 52
}

class Weave_Config():
    MAX_COUNTERS = 114
    MAX_COUNTER_LENGTH = 20
    MAX_FLAGS = 99
    MAX_FLAG_LENGTH = 20
    INITIAL_COUNTERS = 16
    INITIAL_FLAGS = 16
    MAX_KEYBINDS = 8

    DEFAULT_MESSAGES = {
        "bomb": {"touch": "Bomb activated!"},
        "energizer": {"touch": "Energizer - You are invincible"},
        "key": {"touch1": "You now have the ", "touch2": " key.", "fail1": "You already have a ", "fail2": " key!"},
        "door": {"touch1": "The ", "touch2": " door is now open.", "fail1": "The ", "fail2": " door is locked!"},
        "ammo": {"touch": "Ammunition - 5 shots per container."},
        "gem": {"touch": "Gems give you Health!"},
        "torch": {"touch": "Torch - used for lighting in the underground."},
        "invisible": {"touch": "You are blocked by an invisible wall."},
        "forest": {"touch": "A path is cleared through the forest."},
        "fake": {"touch": "A fake wall - secret passage!"},
        "water": {"touch": "Your way is blocked by water."},
        "gameover": {"touch": " Game over  -  Press ESCAPE"},
    }

    DEFAULT_SOUNDS = {
        "bomb": {"touch": "tcf+cf+c", "tick": "t5", "tock": "t8", "explode": "t+++c-c-c-c-c-c"},
        "energizer": {"start": "s.-cd#e", "song": "s.-f+f-fd#c+c-d#e", "end": "s.-c-a#gf#fd#c"},
        "key": {"touch": "t+cegcegceg+sc", "fail": "sc-c"},
        "door": {"touch": "tcgbcgb+ic", "fail": "t--gc"},
        "ammo": {"touch": "tcc#d"},
        "gems": {"touch": "t+c-gec"},
        "torch": {"touch": "tcase", "end": "tc-c-c"},
        "invisible": {"touch": "t--dc"},
        "forest": {"touch": "ta"},
        "water": {"touch": "t+c+c"},
        "gameover": {"touch": "s.-cd#g+c-ga#+dgfg#+cf---w3c"},
    }

    ELEMENT_SPECIFIC_PROPERTIES = {
        "ammo": [
            {"cfg_prop": "p1", "text": "Ammo given"},
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
        "torch": [
            {"cfg_prop": "p1", "text": "Torches Given"},
            {"cfg_prop": "p2", "text": "Wick Given"},
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
        "gem": [
            {"cfg_prop": "p1", "text": "Gems Given"},
            {"cfg_prop": "p2", "text": "Health Given"},
            {"cfg_prop": "scorevalue", "text": "Score Value"},
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
        "key": [
            {"cfg_prop": "p1", "text": "Max Held (Per Color)"},
            {"cfg_prop": "p2", "text": "Character Shift"},
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
        "door": [
            {"cfg_prop": "p2", "text": "Character Shift"},
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
        "passage": [
            {"cfg_prop": "p3", "text": "Default Destination"},
        ],
        "energizer": [
            {"cfg_prop": "p1", "text": "Energized Given"},
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
        "star": [
            {"cfg_prop": "p1", "text": "!!Limited/Eternal"},
            {"cfg_prop": "p2", "text": "Duration"},
        ],
        "bullet": [
            {"cfg_prop": "p1", "text": "!!Limited/Normal"},
            {"cfg_prop": "p2", "text": "Duration"},
            {"cfg_prop": "p3", "text": "Objects Fire Enemy/Player"},
        ],
        "forest": [
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
        "invisible": [
            {"cfg_prop": "p1", "text": "Becomes Element"},
        ],
        "bear": [
            {"cfg_prop": "p1", "text": "Sensitivity"},
            {"cfg_prop": "scorevalue", "text": "Score Value"},
        ],
        "ruffian": [
            {"cfg_prop": "scorevalue", "text": "Score Value"},
            {"cfg_prop": "p1", "text": "Intelligence"},
            {"cfg_prop": "p2", "text": "Resting Time"},
        ],
        "slime": [
            {"cfg_prop": "p2", "text": "Speed"},
        ],
        "shark": [
            {"cfg_prop": "p1", "text": "Intelligence"},
        ],
        "spinninggun": [
            {"cfg_prop": "p1", "text": "Intelligence"},
            {"cfg_prop": "rate", "text": "Firing Rate"},
            {"cfg_prop": "projectile", "text": "Projectile"},
        ],
        "lion": [
            {"cfg_prop": "scorevalue", "text": "Score Value"},
            {"cfg_prop": "p1", "text": "Intelligence"},
        ],
        "tiger": [
            {"cfg_prop": "scorevalue", "text": "Score Value"},
            {"cfg_prop": "p1", "text": "Intelligence"},
            {"cfg_prop": "rate", "text": "Firing Rate"},
            {"cfg_prop": "projectile", "text": "Projectile"},
        ],
        "head": [
            {"cfg_prop": "scorevalue", "text": "Score Value"},
            {"cfg_prop": "p1", "text": "Intelligence"},
            {"cfg_prop": "p2", "text": "Deviance"},
        ],
        "segment": [
            {"cfg_prop": "scorevalue", "text": "Score Value"},
        ],
        "empty": [
            {"cfg_prop": "p1", "text": ""},
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
        "duplicator": [
            {"cfg_prop": "p1", "text": "Speed"},
            {"cfg_prop": "p2", "text": "Starting Phase (0-5)"},
        ],
        "": [
            {"cfg_prop": "p1", "text": ""},
            {"cfg_prop": "p3", "text": "Element Below"},
        ],
    }



    def __init__(self, config=None):
        self.elements = {}
        self.counters = ["X", "Y", "Z",]
        self.flags = []
        self.keybinds = []
        self.initialize_elements()
        self.initialize_messages()
        self.initialize_sounds()
        self.initialize_counters()
        self.initialize_flags()
        self.initialize_keybinds()

    def initialize_elements(self):
        self.elements = {}
        for name in ELEMENT_NAMES:
            self.elements[name] = {
                "fg": None, "bg": None, "char": None, "cycle": None, "canput": None, "pushable": None, "canshoot": None, "walkable": None, "seedark": None, "messages": {}, "sounds": {}
            }
            if Weave_Config.ELEMENT_SPECIFIC_PROPERTIES.get(name):
                self.elements[name]["specific_properties"] = Weave_Config.ELEMENT_SPECIFIC_PROPERTIES[name]

        return True

    def initialize_messages(self):
        print(self.elements)
        for name in ELEMENT_NAMES:
            print("ELEMENT", name)
            to_add = Weave_Config.DEFAULT_MESSAGES.get(name, {})
            for k, v in to_add.items():
                print(name, k, v)
                self.elements[name]["messages"][k] = v
        return True

    def initialize_sounds(self):
        for name in ELEMENT_NAMES:
            to_add = Weave_Config.DEFAULT_SOUNDS.get(name, {})
            for k, v in to_add.items():
                self.elements[name]["sounds"][k] = v
        return True

    def initialize_counters(self):
        while len(self.counters) < Weave_Config.INITIAL_COUNTERS:
            self.counters.append("")
        return True

    def initialize_flags(self):
        while len(self.flags) < Weave_Config.INITIAL_FLAGS:
            self.flags.append("")
        return True

    def initialize_keybinds(self):
        while len(self.keybinds) < Weave_Config.MAX_KEYBINDS:
            self.keybinds.append({"key": "", "text": "", "label": "", "row": 0 })

    def get_all_elements(self):
        for name in ELEMENT_NAMES:
            yield (name, self.elements[name])


class Weave_Setting():
    def __init__(self, **kwargs):
        self.element = kwargs.get("element")
        self.path = kwargs.get("path", "")
        self.kind = kwargs.get("kind", "")
        self.default = kwargs.get("default", "")
        v = kwargs.get("value", "UNSET-VALUE")
        if v is not None and v[0] == '"' and v[-1] == '"':
            v = v[1:-1]
        self.value = v

    def __str__(self):
        return f"<Weave_Setting>{self.element}.{self.path} - {self.value} [{self.kind}]"

    def to_str(self):
        return self.__str__

    def debug_overview(self):
        output = ""
        for p in ["element", "path", "kind", "default"]:
            if hasattr(self, p):
                output += "[" + p + "=" + str(getattr(self, p)) + "] "

        return output

def weave_process_setting(name, path, raw_value):
    #print("PROCESSING", name, path)
    if raw_value is not None:
        raw_value = raw_value.strip()
    #print(name, ":", path, "RAW_VALUE:", raw_value)
    w_setting = Weave_Setting(element=name, path=path, value=weave_process_value(raw_value), kind=weave_get_kind(path), default=weave_get_default(path))
    return w_setting

def weave_process_value(raw_value):
    return raw_value

def weave_get_kind(path):
    if path.startswith("msg") or path.endswith("msg") or path.endswith("label") or path in ["object.name", "scroll.name", "titleprompt", "sound.label.on", "sound.label.off", "health", "ammo", "torches", "gems", "score", "keys", "time"]:
        return "W_STRING"
    if path.startswith("snd"):
        return "W_SOUND"
    if path.startswith("fg") or path.startswith("bg"):
        return "W_COLOR"
    if path in ["char", "cycle", "p1", "p2", "p3", "torchsize", "bombsize", "maxoop", "ouchdamage", "graceperiod", "friendlyfire", "startboard", "footsteps", "highscores"] or path in ["scorevalue", "counter"] or path.startswith("torchratio") or path.startswith("bombratio"):
        return "W_INTEGER"
    if path in ["pushable", "walkable", "seedark", "canput", "canshoot", "blinking"]:
        return "W_BOOL"
    if path == "flag":
        return "W_FLAG"
    if path.endswith("bind"):
        return "W_BIND"
    if path.endswith(".counter"):  # Intended for sidebar.X.counter
        return "W_SIDEBAR_COUNTER"
    if path in COLORS:
        return "W_PALETTE"
    if path.endswith("sidebar.row"):
        return "W_SIDEBAR_ROW"

def weave_get_default(path):
    return "DEFAULT: " + path

def weave_get_initial_config():
    print("This is called right")
    all_settings = {}
    processed_elements = []
    config_file_path = "/home/drdos/projects/museum-of-zzt/museum_site/static/data/TEMPLATE.CFG"  # TODO
    with open(config_file_path) as fh:
        lines = fh.readlines()

    for line in lines:
        if line.startswith("#"):
            continue
        line = line.strip()

        (full_key, raw_value) = line.split("=", 1)
        #print(full_key, raw_value)

        # Process full_key
        (name, path) = full_key.split(".", 1)
        path = path.strip()

        if not all_settings.get(name):
            all_settings[name] = {}
            processed_elements.append(name)

        print("Logging setting", name, path)
        all_settings[name][path] = weave_process_setting(name, path, raw_value)

    # Custom text is commented out by default. Probably because it's weird.
    all_settings["customtext"] = {}

    # Add missing universal keys
    for element_name in ELEMENT_NAMES:
        keys = []
        for prop, value in all_settings[element_name].items():
            keys.append(value.path)
        for uni_key in ["fg", "bg", "canshoot", "canput", "walkable", "pushable", "seedark"]:
            if uni_key not in keys:
                #print("ELEMENT", element_name, "IS MISSING", uni_key)
                all_settings[element_name][uni_key] = weave_process_setting(element_name, uni_key, None)

    """
    for k, props in all_settings.items():
        for p in props:
            if p.kind == None:
                print("UNHANDLED KIND", k, p.debug_overview())
            else:
                print("\t\t", k, p.debug_overview())
    """
    return all_settings
