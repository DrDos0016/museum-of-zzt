import { Character_Set } from "./character_set.js";
import { Palette } from "./palette.js";

export class ZZT_Standard_Renderer
{
    constructor(fvpk=null)
    {
        this.name = "ZZT Standard Renderer";
        this.fvpk = fvpk;
        this.board_width = 60;
        this.board_height = 25;
        this.show_border = false; // Render that border
        this.character_set = new Character_Set();
        this.palette = new Palette();
        this.tick = 0;
        this.default_characters = [32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 179, 92, 248, 176, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 62, 249, 42, 205, 153, 5, 2, 42, 94, 24, 16, 234, 227, 186, 233, 79, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63];
        this.element_func = Array(256).fill(this.basic_draw);

        this.element_func[0] = this.empty_draw;
        this.element_func[12] = this.duplicator_draw;
        this.element_func[13] = this.bomb_draw;
        this.element_func[15] = this.star_draw;
        this.element_func[16] = this.conveyor_cw_draw;
        this.element_func[17] = this.conveyor_ccw_draw;
        this.element_func[30] = this.transporter_draw;
        this.element_func[31] = this.line_draw;
        this.element_func[36] = this.object_draw;
        this.element_func[39] = this.spinning_gun_draw;
        this.element_func[40] = this.pusher_draw;
        this.element_func.fill(this.text_draw, 47);

        this.default_stat = {"x": 0, "y": 0, "step_x": 0, "step_y": 0, "cycle": 0, "param1": 0, "param2": 0, "param3": 0, "follow": -1, "leader": -1};

        this.ctx = null;
    }

    async render_board(board, zoom=1)
    {
        console.log("TOLD TO RENDER BOARD", board);
        if (! this.character_set.loaded)
            await this.character_set.load();
        this.rendered_board = board;

        console.log("Charset loaded, back in render board");

        console.log("Rendering a board (this.fvpk)", this.fvpk);
        //const canvas = document.createElement("canvas");
        const canvas = document.querySelector(`#envelope-${this.fvpk} .fv-canvas`);
        let new_width = (this.board_width + (2 * this.show_border)) * this.character_set.tile_width;
        let new_height = (this.board_height + (2 * this.show_border)) * this.character_set.tile_height;
        canvas.setAttribute("width", new_width + "px");
        canvas.setAttribute("height", new_height + "px");
        canvas.setAttribute("class", `fv-canvas fv-canvas-zoom-${zoom}`);

        //canvas.insertAdjacentHTML("afterend", "Is this real?");

        this.ctx = canvas.getContext("2d");

        for (let y = 1; y < 26; y++)
        {
            for (let x = 1; x < 61; x++)
            {
                let [fg, bg, char] = this.element_func[this.rendered_board.elements[x][y].id].apply(this, [x, y]);
                this.stamp(x, y, fg, bg, char);
            }
        }
        return canvas;
    }

    stamp(x, y, fg, bg, char)
    {
        const border_offset = (! this.show_border);
        let ch_x = char % 16;
        let ch_y = parseInt(char / 16);
        // Background
            this.ctx.globalCompositeOperation = "source-over";
            this.ctx.fillStyle = bg;
            this.ctx.fillRect((x - border_offset) * this.character_set.tile_width, (y - border_offset) * this.character_set.tile_height, this.character_set.tile_width, this.character_set.tile_height);

            // Foreground transparency
            this.ctx.globalCompositeOperation = "xor";
            this.ctx.drawImage(
                this.character_set.image,
                ch_x * this.character_set.tile_width,
                ch_y * this.character_set.tile_height,
                this.character_set.tile_width,
                this.character_set.tile_height,
                (x - border_offset) * this.character_set.tile_width,
                (y - border_offset) * this.character_set.tile_height,
                this.character_set.tile_width,
                this.character_set.tile_height
            );

            // Foreground
            this.ctx.globalCompositeOperation = "destination-over";
            this.ctx.fillStyle = fg;
            this.ctx.fillRect(
                (x - border_offset) * this.character_set.tile_width,
                (y - border_offset) * this.character_set.tile_height,
                this.character_set.tile_width, this.character_set.tile_height
            ); // -1 for border compensation
    }

    crosshair(center_x, center_y, state="on")
    {
        if (state == "on")
        {

            if (center_x < 0 || center_y < 0 || center_x > this.board_width || center_y > this.board_height)
                return false;

            let x = center_x - 1;
            let y = center_y - 1;

            if (! this.show_border)
            {
                x -= 1;
                y -= 1;
            }

            let border_w = this.character_set.tile_width;
            let border_h = this.character_set.tile_height;

            $(".crosshair").css(
            {
                "width": border_w + "px",
                "height": border_h + "px",
                "border-top": `${border_h}px solid #FFD700`,
                "border-right": `${border_w}px solid #FFD700`,
                "border-bottom": `${border_h}px solid #FFD700`,
                "border-left": `${border_w}px solid #FFD700`,
                "margin-top": `${y * this.character_set.tile_height}px`,
                "margin-left": `${x * this.character_set.tile_width}px`,
            });
            return true;
        }

        $(".crosshair").css(
        {
            "width": "0px",
            "height": "0px",
            "border-top": "0px",
            "border-right": "0px",
            "border-bottom": "0px",
            "border-left": "0px",
            "margin-top": "0px",
            "margin-left": "0px",
        });
    }

    get_stats_for_element(x, y, limit=1)
    {
        // Returns an array to support stat-stacking.
        let output = [];
        let matches = 0;
        for (let idx = 0; idx < this.rendered_board.stats.length; idx++)
        {
            if (this.rendered_board.stats[idx].x == x && this.rendered_board.stats[idx].y == y)
            {
                output.push(this.rendered_board.stats[idx])
                matches++;
            }
            if (matches >= limit)
                break;
        }

        if (output.length == 0) // This element is statless
        {
            return [this.default_stat];
        }
        return output;
    }

    basic_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], this.default_characters[element.id]];
    }

    empty_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        return [this.palette.hex_colors[0], this.palette.hex_colors[0], this.default_characters[element.id]];
    }

    text_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        if (element.id == 53) // White text gets black background instead of gray
            return [this.palette.hex_colors[15], this.palette.hex_colors[0], element.color]
        return [this.palette.hex_colors[15], this.palette.hex_colors[(element.id - 46) % 16], element.color]; // mod 16 to handle undefined elements
    }

    pusher_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        if (stat.step_x == 1)
            char = 16;
        else if (stat.step_x == -1)
            char = 17;
        else if (stat.step_y == -1)
            char = 30;
        else
            char = 31;

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    duplicator_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        switch (stat.param1) {
            case 1: char = 250; break;
            case 2: char = 249; break;
            case 3: char = 248; break;
            case 4: char = 111; break;
            case 5: char = 79; break;
            default: char = 250;
        }

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    bomb_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        if (stat.param1 <= 1)
            char = 11
        else
            char = (48 + stat.param1) % 256;

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    star_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        let animation_characters = [179, 47, 196, 92];
        char = animation_characters[this.tick % 4];
        element.color = element.color + 1;
        if (element.color > 15)
            element.color = 9;

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    conveyor_cw_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        switch (parseInt(this.tick / 3) % 4) {  // Divide by default cycle per element defintions table
            case 0: char = 179; break;
            case 1: char = 247; break;
            case 2: char = 196; break;
            default: char = 92;
        }

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    conveyor_ccw_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        switch (parseInt(this.tick / 2) % 4) {  // Divide by default cycle per element defintions table
            case 3: char = 179; break;
            case 2: char = 47; break;
            case 1: char = 196; break;
            default: char = 92;
        }

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    transporter_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char = stat.param1;
        let animation_characters = {"ns": [94, 126, 94, 45, 118, 95, 118, 45], "ew": [40, 60, 40, 179, 41, 62, 41, 179]};

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        if (stat.cycle == 0)
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 33];

        if (stat.step_x == 0)
            char = animation_characters.ns[stat.step_y * 2 + 2 + parseInt(this.tick / stat.cycle) % 4];
        else
            char = animation_characters.ew[stat.step_x * 2 + 2 + parseInt(this.tick / stat.cycle) % 4];

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    line_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let line_chars = [249, 208, 210, 186, 181, 188, 187, 185, 198, 200, 201, 204, 205, 202, 203, 206];
        let line_idx = 0
        line_idx += (this.rendered_board.elements[x][y - 1].id == 31 || this.rendered_board.elements[x][y - 1].id == 1) ? 1 : 0;  // N
        line_idx += (this.rendered_board.elements[x][y + 1].id == 31 || this.rendered_board.elements[x][y + 1].id == 1) ? 2 : 0;  // S
        line_idx += (this.rendered_board.elements[x - 1][y].id == 31 || this.rendered_board.elements[x - 1][y].id == 1) ? 4 : 0;  // W
        line_idx += (this.rendered_board.elements[x + 1][y].id == 31 || this.rendered_board.elements[x + 1][y].id == 1) ? 8 : 0;  // E

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], line_chars[line_idx]];
    }

    object_draw(x, y)
    {
        let element, stat, char;
        element = this.rendered_board.elements[x][y];

        try
        {
            stat = this.get_stats_for_element(x, y)[0];
            char = stat.param1;
        }
        catch (error)
        {
            char = 2; // TODO Magic Num
        }

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    spinning_gun_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let char;

        switch (this.tick % 8) {
            case 0:
            case 1: char = 24; break;
            case 2:
            case 3: char = 26; break;
            case 4:
            case 5: char = 25; break;
            default: char = 27;
        }

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }
}
