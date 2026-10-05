ELEMENT_NAMES = ["ammo", "bear", "blinkew", "blinkns", "blinkwall", "bluetext", "bomb", "boulder", "breakable", "bullet", "customtext", "cyantext", "darkness", "door", "duplicator", "edge", "empty", "energizer", "fake", "forest", "gem", "greentext", "head", "invisible", "key", "lion", "monitor", "normal", "passage", "player", "purpletext", "redtext", "ricochet", "ruffian", "scroll", "segment", "shark", "sliderew", "sliderns", "slime", "solid", "spinninggun", "star", "tiger", "torch", "transporter", "water", "whitetext", "yellowtext", ]

COLORS = ["black", "dkblue", "dkgreen", "dkcyan", "dkred", "dkpurple", "brown", "gray", "dkgray", "blue", "green", "cyan", "red", "purple", "yellow", "white"]

class Weave_Config():
    def __init__(self, config):
        self.config = config
        print("////////////////////// WC Init")
        print(list(self.config["ammo"].keys()))
        #self.foobar()
        self.process_section("msg")
        self.process_section("snd")

    def get_all_elements(self):
        for name in ELEMENT_NAMES:
            yield (name, self.config[name])

    def process_section(self, to_process):
        print("PROCESSING SECTION", to_process)
        for name in ELEMENT_NAMES:
            self.config[name][to_process] = []
            for k in self.config[name].keys():
                if k == to_process:  # This prevents keys being added for "msg" and "snd". IDK why they're being added!
                    continue
                if name == "ammo":
                    print("\tSCANNING NAME/KEY", name, k, "TOPROC", to_process)
                if k.startswith(to_process):
                    element = self.config[name][k]
                    if element:
                        print("ADDING FULL PATH", name + "." + k, "WITH VALUE", getattr(element, "value", ""))
                        self.config[name][to_process].append({"full_path": name + "." + k, "path": k, "label": k.split(".")[-1], "value": getattr(element, "value", "")})

    def foobar(self):
        for name in ELEMENT_NAMES:
            self.config[name]

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
    config_file_path = "/home/drdos/projects/museum-of-zzt/tools/TEMPLATE.CFG"  # TODO
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

        #print("Logging setting", name, path)
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
