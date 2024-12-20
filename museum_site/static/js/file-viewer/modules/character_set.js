import { CHARACTER_SETS } from "./core.js";

export class Character_Set
{
    constructor()
    {
        this.name = "";
        //this.path = "/static/js/file-viewer/res/charset/cp437.png";
        this.path = "";
        this.loaded = false;
        this.image = null;
        this.tile_width = 8;
        this.tile_height = 14;
        this.CHARSET_BASE_PATH = "/static/js/file-viewer/res/charset/";
    }

    async load(name="cp437.png")
    {
        let image;
        console.log("LOADING A CHARSET:", name);

        if (name.startsWith("fvpk-"))
        {
            console.log("It's an FVPK", name);
            image = await this.load_charset_from_fvpk(CHARACTER_SETS[name])
        }
        else if (name.toUpperCase().endsWith(".PNG"))
            image = await this.load_charset_from_png(name);
        else if (name.toUpperCase().endsWith(".CHR"))
            image = await this.load_charset_from_chr(name);

        console.log("Loaded charset:", name);
        this.image = image;
        this.loaded = true;
        return true;
    }

    async load_charset_from_png(name)
    {
        console.log("Using png", name, "from path", this.CHARSET_BASE_PATH + name);
        let image;
        const promise = new Promise(resolve => {
            image = new Image();
            image.onload = resolve;
            image.src = this.CHARSET_BASE_PATH + name;
        });

        await promise;
        return image;
    }

    async load_charset_from_chr(name)
    {
        console.log("Using chr", name, "from path", this.CHARSET_BASE_PATH + name);
        let image;
        await fetch(this.CHARSET_BASE_PATH + name).then(response => response.arrayBuffer()).then(data => this.parse_chr(data));
        const promise = new Promise(resolve => {
            image = new Image();
            image.onload = resolve;
            image.src = this.canvas.toDataURL();
        });
        return image;
    }

    async load_charset_from_fvpk(charset)
    {
        // TODO: Assumes .CHR only
        console.log("Loading from FVPK", charset);
        let image;
        this.parse_chr(charset.bytes);
        const promise = new Promise(resolve => {
            image = new Image();
            image.onload = resolve;
            image.src = this.canvas.toDataURL();
        });
        return image;
    }

    parse_chr(data)
    {
        console.log("Parse chr func");
        this.data = new DataView(data); // Turn ArrayBuffer into DataView
        this.pos = 0;

        let canvas = document.createElement("canvas");
        canvas.width = (16 * this.tile_width);
        canvas.height = (16 * this.tile_height);
        let ctx = canvas.getContext("2d");
        ctx.imageSmoothingEnabled = false;
        ctx.strokeStyle = "#00FF00";
        ctx.fillStyle = "#00000000";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#FFFFFF";

        let x = 0; // Origin coords of character
        let y = 0;
        let ch = 0
        let x_offset = 0;
        let y_offset = 0;

        while (ch < 255) // Characters
        {
            x_offset = 0;
            y_offset = 0;

            if ((ch != 0) && (ch % 16 == 0))
            {
                y += this.tile_height;
                x = 0;
            }

            // Rows
            for (let row_idx = 0; row_idx < this.tile_height; row_idx++)
            {
                x_offset = 0;
                let row = this.read_Uint8();
                let bits = ("00000000" + row.toString(2)).slice(-8);

                // Columns
                for (let idx in bits)
                {
                    if (bits[idx] == "1")
                        ctx.fillRect(x + x_offset, y + y_offset, 1, 1);
                    x_offset += 1;
                }
                y_offset += 1;
            }
            x += this.tile_width;
            ch++;
        }

        // Parsing complete
        this.canvas = canvas;
        return true;
    }

    read_Uint8()
    {
        var output = this.data.getUint8(this.pos);
        try {
            var output = this.data.getUint8(this.pos);
        } catch (e) {
            var output = 0;
        }
        this.pos += 1;
        return output;
    }
}

export const CHAR = {
    "SMILEY": 2,
    "GEM": 4,
    "RUFFIAN": 5,
    "DOOR": 10,
    "BOMB": 11,
    "KEY": 12,
    "PUSHER": 16,
    "SLIDER_NS": 18,
    "SPINNING_GUN": 24,
    "SLIDER_EW": 29,
    "SPACE": 32,
    "RICOCHET": 42,
    "CLOCKWISE": 47,
    "SLIME": 42,
    "TRANSPORTER": 62,
    "QUESTION_MARK": 63,
    "SEGMENT": 79,
    "COUNTER": 92,
    "SHARK": 94,
    "ENERGIZER": 127,
    "AMMO": 132,
    "BEAR": 153,
    "TORCH": 157,
    "WATER": 176,
    "FOREST": 176,
    "BREAKABLE": 177,
    "NORMAL": 178,
    "FAKE": 178,
    "STAR": 83,
    "VERT_RAY": 186,
    "HORIZ_RAY": 205,
    "BLINKWALL": 206,
    "SOLID": 219,
    "TIGER": 227,
    "SCROLL": 232,
    "HEAD": 233,
    "LION": 234,
    "PASSAGE": 240,
    "BULLET": 248,
    "LINE": 249,
    "DUPLICATOR": 250,
    "BOULDER": 254,
    "LAVA": 9,
    "FLOOR": 176,
    "WATER_N": 30,
    "WATER_S": 31,
    "WATER_W": 17,
    "WATER_E": 16,
    "ROTON": 148,
    "DRAGON_PUP": 237,
    "PAIRER": 237,
    "SPIDER": 15,
    "WEB": 197,
    "STONE": 90,
};
