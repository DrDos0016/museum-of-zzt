export class Character_Set
{
    constructor()
    {
        this.name = "Codepage 437";
        this.path = "/static/js/file-viewer/res/charset/cp437.png";
        this.loaded = false;
        this.image = null;
        this.tile_width = 8;
        this.tile_height = 14;
    }

    async load()
    {
        let image;
        const promise = new Promise(resolve => {
            image = new Image();
            image.onload = resolve;
            image.src = this.path;
        });

        await promise;
        console.log("Loaded charset");
        this.image = image;
        this.loaded = true;
        return true;
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
};
