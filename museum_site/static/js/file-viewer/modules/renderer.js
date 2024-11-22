import { Character_Set, CHAR } from "./character_set.js";
import { Palette, COLOR } from "./palette.js";

export class ZZT_Standard_Renderer
{
    constructor(fvpk=null)
    {
        this.name = "ZZT Standard Renderer";
        this.fvpk = fvpk;
        this.board_width = 60;
        this.board_height = 25;
        this.character_set = new Character_Set();
        this.palette = new Palette();
        this.default_characters = [CHAR.SPACE, CHAR.SPACE, CHAR.QUESTION_MARK, CHAR.SPACE, CHAR.SMILEY, CHAR.AMMO, CHAR.TORCH, CHAR.GEM, CHAR.KEY, CHAR.DOOR, CHAR.SCROLL, CHAR.PASSAGE, CHAR.DUPLICATOR, CHAR.BOMB, CHAR.ENERGIZER, CHAR.STAR, CHAR.CLOCKWISE, CHAR.COUNTER, CHAR.BULLET, CHAR.WATER, CHAR.FOREST, CHAR.SOLID, CHAR.NORMAL, CHAR.BREAKABLE, CHAR.BOULDER, CHAR.SLIDER_NS, CHAR.SLIDER_EW, CHAR.FAKE, CHAR.SPACE, CHAR.BLINKWALL, CHAR.TRANSPORTER, CHAR.LINE, CHAR.RICOCHET, CHAR.HORIZ_RAY, CHAR.BEAR, CHAR.RUFFIAN, CHAR.SMILEY, CHAR.SLIME, CHAR.SHARK, CHAR.SPINNING_GUN, CHAR.PUSHER, CHAR.LION, CHAR.TIGER, CHAR.VERT_RAY, CHAR.HEAD, CHAR.SEGMENT, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK];

        this.element_func = this.initialize_renderer_draw_functions();
        this.default_stat = {"x": 0, "y": 0, "step_x": 0, "step_y": 0, "cycle": 0, "param1": 0, "param2": 0, "param3": 0, "follow": -1, "leader": -1, "oop": ""};

        this.ctx = null;
    }

    static initial_config = {
        "appearance": {
            "show_high_intensity_backgrounds": false,
            "invisible_wall": 0,
            "empty": 0,
            "monitor": 0,
            "edge": 0,
            "show_outer_border": false, // TODO: Is this even a feature worth supporting
        },
        "game": {
            "tick": 0,
        },
    }

    initialize_renderer_draw_functions()
    {
        let element_func = Array(256).fill(this.basic_draw);

        element_func[0] = this.empty_draw;
        element_func[1] = this.edge_draw;
        element_func[3] = this.monitor_draw;
        element_func[12] = this.duplicator_draw;
        element_func[13] = this.bomb_draw;
        element_func[15] = this.star_draw;
        element_func[16] = this.conveyor_cw_draw;
        element_func[17] = this.conveyor_ccw_draw;
        element_func[28] = this.invisible_draw;
        element_func[30] = this.transporter_draw;
        element_func[31] = this.line_draw;
        element_func[36] = this.object_draw;
        element_func[39] = this.spinning_gun_draw;
        element_func[40] = this.pusher_draw;
        element_func.fill(this.text_draw, 47);

        return element_func;
    }

    get_preferences()
    {
        let output = "<h3>Renderer Options</h3>";
        let config_key = "renderer";

        output += `<div class="field-wrapper">
            <label for="">High Intensity <u>B</u>ackgrounds:</label>
            <div class="field-value"><select data-config="zzt_handler.${config_key}.appearance.show_high_intensity_backgrounds" data-type="int">
                <option value=1${(this.config.appearance.show_high_intensity_backgrounds == true) ? " selected" : ""}>On</option>
                <option value=0${(this.config.appearance.show_high_intensity_backgrounds == false) ? " selected" : ""}>Off*</option>
            </select></div>
            <p class="field-help">Render bright background colors. Toggle at any time with <span class="mono">Shift + B</span>.</p>
        </div>`;

        output += `<div class="field-wrapper">
            <label for="">Invisible Wall Appearance:</label>
            <div class="field-value"><select data-config="zzt_handler.${config_key}.appearance.invisible_wall" data-type="int">
                <option value=0${(this.config.appearance.invisible_wall == 0) ? " selected" : ""}>Visible - Editor Style*</option>
                <option value=1${(this.config.appearance.invisible_wall == 1) ? " selected" : ""}>Invisible - Gameplay Style</option>
                <option value=2${(this.config.appearance.invisible_wall == 2) ? " selected" : ""}>Revealed - Gameplay Style</option>
            </select></div>
            <p class="field-help">Render bright background colors.</p>
        </div>`;

        output += `<div class="field-wrapper">
            <label for="">Empty Appearance:</label>
            <div class="field-value"><select data-config="zzt_handler.${config_key}.appearance.empty" data-type="int">
                <option value=0${(this.config.appearance.empty == 0) ? " selected" : ""}>&nbsp; - Invisible*</option>
                <option value=1${(this.config.appearance.empty == 1) ? " selected" : ""}>• - Visible</option>
                <option value=2${(this.config.appearance.empty == 2) ? " selected" : ""}>A - Render As Text</option>
            </select></div>
            <p class="field-help">Render empties invisibly, visibly, or as text to reveal erased text in some worlds.</p>
        </div>`;

        output += `<div class="field-wrapper">
            <label for="">Monitor Appearance:</label>
            <div class="field-value"><select data-config="zzt_handler.${config_key}.appearance.monitor" data-type="int">
                <option value=0${(this.config.appearance.monitor == 0) ? " selected" : ""}>M - KevEdit Style*</option>
                <option value=1${(this.config.appearance.monitor == 1) ? " selected" : ""}>Hidden - ZZT Style</option>
            </select></div>
            <p class="field-help">Render bright background colors.</p>
        </div>`;

        output += `<div class="field-wrapper">
            <label for="">Board Edge Appearance:</label>
            <div class="field-value"><select data-config="zzt_handler.${config_key}.appearance.edge" data-type="int">
                <option value=0${(this.config.appearance.edge == 0) ? " selected" : ""}>E - KevEdit Style*</option>
                <option value=1${(this.config.appearance.edge == 1) ? " selected" : ""}>Hidden - ZZT Style</option>
            </select></div>
            <p class="field-help">Render bright background colors.</p>
        </div>`;
        return output;
    }

    async render_board(board, zoom=1)
    {
        if (! board)
        {
            const canvas = document.querySelector(`#envelope-${this.fvpk} .fv-canvas`);
            this.ctx = canvas.getContext("2d");
            this.ctx.fillStyle = "#AA0000";
            this.ctx.fillRect(0, 0, canvas.width, canvas.height);
            return canvas;
        }

        console.log("TOLD TO RENDER BOARD", board);
        if (! this.character_set.loaded)
            await this.character_set.load();
        this.rendered_board = board;

        console.log("Charset loaded, back in render board");

        console.log("Rendering a board (this.fvpk)", this.fvpk);
        const canvas = document.querySelector(`#envelope-${this.fvpk} .fv-canvas`);
        let new_width = (this.board_width + (2 * this.config.appearance.show_outer_border)) * this.character_set.tile_width;
        let new_height = (this.board_height + (2 * this.config.appearance.show_outer_border)) * this.character_set.tile_height;
        canvas.setAttribute("width", new_width + "px");
        canvas.setAttribute("height", new_height + "px");
        canvas.setAttribute("class", `fv-canvas fv-canvas-zoom-${zoom}`);

        this.ctx = canvas.getContext("2d");

        for (let y = 1; y < (this.board_height + 1); y++)
        {
            for (let x = 1; x < (this.board_width + 1); x++)
            {
                let [fg, bg, char] = this.element_func[this.rendered_board.elements[x][y].id].apply(this, [x, y]);
                [fg, bg, char] = this.post_process(x, y, fg, bg, char, this.rendered_board.elements[x][y].id);
                this.stamp(x, y, fg, bg, char);
            }
        }
        return canvas;
    }

    post_process(x, y, fg, bg, char, id) { return [fg, bg, char] };

    stamp(x, y, fg, bg, char)
    {
        const border_offset = (! this.config.appearance.show_outer_border);
        let ch_x = char % 16;
        let ch_y = parseInt(char / 16);

        // High Intensity Check
        if (! this.config.appearance.show_high_intensity_backgrounds)
            bg %= 8; // Reduce to lower half of palette

        let fg_hex = this.palette.hex_colors[fg];
        let bg_hex = this.palette.hex_colors[bg];

        // Background
        this.ctx.globalCompositeOperation = "source-over";
        this.ctx.fillStyle = bg_hex;
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
        this.ctx.fillStyle = fg_hex;
        this.ctx.fillRect(
            (x - border_offset) * this.character_set.tile_width,
            (y - border_offset) * this.character_set.tile_height,
            this.character_set.tile_width, this.character_set.tile_height
        ); // -1 for border compensation
    }

    crosshair(center_x, center_y, state="on")
    {
        let zoom = $(`#envelope-${this.fvpk} .fv-canvas`).hasClass("fv-canvas-zoom-2") ? 2 : 1; // Assume 1/2 only
        if (state == "on")
        {

            if (center_x < 0 || center_y < 0 || center_x > this.board_width || center_y > this.board_height)
                return false;

            let x = center_x - 1;
            let y = center_y - 1;

            if (! this.config.appearance.show_outer_border)
            {
                x -= 1;
                y -= 1;
            }

            let border_w = this.character_set.tile_width * zoom;
            let border_h = this.character_set.tile_height * zoom;
            let zoom_comp_top = (zoom == 2) ? 5 : 0; // Compensate for zoom being centered
            let zoom_comp_left = (zoom == 2) ? -240 : 0; // Ditto

            $(".crosshair").css(
            {
                "width": border_w + "px",
                "height": border_h + "px",
                "border-top": `${border_h}px solid #FFD700`,
                "border-right": `${border_w}px solid #FFD700`,
                "border-bottom": `${border_h}px solid #FFD700`,
                "border-left": `${border_w}px solid #FFD700`,
                "margin-top": `${y * this.character_set.tile_height * zoom + zoom_comp_top}px`,
                "margin-left": `${x * this.character_set.tile_width * zoom + zoom_comp_left}px`,
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
        return [element.color % 16, parseInt(element.color / 16), this.default_characters[element.id]];
    }

    empty_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        switch (this.config.appearance.empty)
        {
            case 1: // Visible
                return [element.color % 16, parseInt(element.color / 16), 7];
            case 2: // Text
                return [7, 0, element.color];
            default: // Invisible
                return [0, 0, this.default_characters[element.id]];
        }
    }

    text_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        if (element.id == 53) // White text gets black background instead of gray
            return [15, 0, element.color]
        return [15, (element.id - 46) % 16, element.color]; // mod 16 to handle undefined elements
    }

    pusher_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [element.color % 16, parseInt(element.color / 16), 63];

        if (stat.step_x == 1)
            char = 16;
        else if (stat.step_x == -1)
            char = 17;
        else if (stat.step_y == -1)
            char = 30;
        else
            char = 31;

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    duplicator_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [element.color % 16, parseInt(element.color / 16), 63];

        switch (stat.param1) {
            case 1: char = 250; break;
            case 2: char = 249; break;
            case 3: char = 248; break;
            case 4: char = 111; break;
            case 5: char = 79; break;
            default: char = 250;
        }

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    bomb_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [element.color % 16, parseInt(element.color / 16), 63];

        if (stat.param1 <= 1)
            char = 11
        else
            char = (48 + stat.param1) % 256;

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    star_draw(x, y)
    {
        // TODO STAR CHARACTERS HAVE NOTHING TO DO WITH STATS
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [element.color % 16, parseInt(element.color / 16), 63];

        let animation_characters = [179, 47, 196, 92];
        char = animation_characters[this.config.game.tick % 4];
        element.color = element.color + 1;
        if (element.color > 15)
            element.color = 9;

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    conveyor_cw_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [element.color % 16, parseInt(element.color / 16), 63];

        switch (parseInt(this.config.game.tick / 3) % 4) {  // Divide by default cycle per element defintions table
            case 0: char = 179; break;
            case 1: char = 247; break;
            case 2: char = 196; break;
            default: char = 92;
        }

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    conveyor_ccw_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char;

        if (typeof stat == "undefined")
            return [element.color % 16, parseInt(element.color / 16), 63];

        switch (parseInt(this.config.game.tick / 2) % 4) {  // Divide by default cycle per element defintions table
            case 3: char = 179; break;
            case 2: char = 47; break;
            case 1: char = 196; break;
            default: char = 92;
        }

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    transporter_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let stat = this.get_stats_for_element(x, y)[0];
        let char = stat.param1;
        let animation_characters = {"ns": [94, 126, 94, 45, 118, 95, 118, 45], "ew": [40, 60, 40, 179, 41, 62, 41, 179]};

        if (typeof stat == "undefined")
            return [element.color % 16, parseInt(element.color / 16), 63];

        if (stat.cycle == 0)
            return [element.color % 16, parseInt(element.color / 16), 33];

        if (stat.step_x == 0)
            char = animation_characters.ns[stat.step_y * 2 + 2 + parseInt(this.config.game.tick / stat.cycle) % 4];
        else
            char = animation_characters.ew[stat.step_x * 2 + 2 + parseInt(this.config.game.tick / stat.cycle) % 4];

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    line_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let line_chars = this.get_line_chars(element.id);
        let line_idx = 0
        line_idx += (this.rendered_board.elements[x][y - 1].id == element.id || this.rendered_board.elements[x][y - 1].id == 1) ? 1 : 0;  // N
        line_idx += (this.rendered_board.elements[x][y + 1].id == element.id || this.rendered_board.elements[x][y + 1].id == 1) ? 2 : 0;  // S
        line_idx += (this.rendered_board.elements[x - 1][y].id == element.id || this.rendered_board.elements[x - 1][y].id == 1) ? 4 : 0;  // W
        line_idx += (this.rendered_board.elements[x + 1][y].id == element.id || this.rendered_board.elements[x + 1][y].id == 1) ? 8 : 0;  // E

        return [element.color % 16, parseInt(element.color / 16), line_chars[line_idx]];
    }

    get_line_chars(id)
    {
        return [249, 208, 210, 186, 181, 188, 187, 185, 198, 200, 201, 204, 205, 202, 203, 206];
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

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    spinning_gun_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let char;

        switch (this.config.game.tick % 8) {
            case 0:
            case 1: char = 24; break;
            case 2:
            case 3: char = 26; break;
            case 4:
            case 5: char = 25; break;
            default: char = 27;
        }

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    invisible_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let char;

        switch (this.config.appearance.invisible_wall)
        {
            case 0:
                char = 176;
                break;
            case 2:
                char =  178;
                break;
            default:
                char = this.default_characters[element.id];
                break;
        }

        return [element.color % 16, parseInt(element.color / 16), char];
    }

    monitor_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let char = (this.config.appearance.monitor) ? this.default_characters[element.id] : 77;
        return [element.color % 16, parseInt(element.color / 16), char];
    }

    edge_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        let char = (this.config.appearance.edge) ? this.default_characters[element.id] : 69;
        return [element.color % 16, parseInt(element.color / 16), char];
    }
}


export class ZZT_Object_Highlight_Renderer extends ZZT_Standard_Renderer
{
    constructor(fvpk=null)
    {
        super(fvpk);
        this.name = "ZZT Object Highlight Renderer";
    }

    post_process(x, y, fg, bg, char, id)
    {
        if (id == 36)
            return [14, 4, 33];
        else
        {
            return [8, 0, char];
        }
    }
}


export class ZZT_Code_Highlight_Renderer extends ZZT_Standard_Renderer
{
    constructor(fvpk=null)
    {
        super(fvpk);
        this.name = "ZZT Code Highlight Renderer";
    }

    post_process(x, y, fg, bg, char, id)
    {
        let stat = this.get_stats_for_element(x, y)[0];
        if (stat.oop)
            return [14, 4, 33];
        else
            return [8, 0, char];
    }
}


export class ZZT_Fake_Wall_Highlight_Renderer extends ZZT_Standard_Renderer
{
    constructor(fvpk=null)
    {
        super(fvpk);
        this.name = "ZZT Fake Wall Highlight Renderer";
    }

    post_process(x, y, fg, bg, char, id)
    {
        if (id == 27)
            return [14, 4, 178];
        else
            return [8, 0, char];
    }
}

export class SZZT_Standard_Renderer extends ZZT_Standard_Renderer
{
    constructor(fvpk=null)
    {
        super(fvpk);
        this.name = "Super ZZT Standard Renderer";
        this.fvpk = fvpk;
        this.board_width = 96;
        this.board_height = 80;
        this.character_set = new Character_Set();
        this.palette = new Palette();
        this.default_characters = [CHAR.SPACE, CHAR.SPACE, CHAR.QUESTION_MARK, CHAR.SPACE, CHAR.SMILEY, CHAR.AMMO, CHAR.QUESTION_MARK, CHAR.GEM, CHAR.KEY, CHAR.DOOR, CHAR.SCROLL, CHAR.PASSAGE, CHAR.DUPLICATOR, CHAR.BOMB, CHAR.ENERGIZER, CHAR.QUESTION_MARK, CHAR.CLOCKWISE, CHAR.COUNTER, CHAR.QUESTION_MARK, CHAR.LAVA, CHAR.FOREST, CHAR.SOLID, CHAR.NORMAL, CHAR.BREAKABLE, CHAR.BOULDER, CHAR.SLIDER_NS, CHAR.SLIDER_EW, CHAR.FAKE, CHAR.SPACE, CHAR.BLINKWALL, CHAR.TRANSPORTER, CHAR.LINE, CHAR.RICOCHET, CHAR.QUESTION_MARK, CHAR.BEAR, CHAR.RUFFIAN, CHAR.SMILEY, CHAR.SLIME, CHAR.SHARK, CHAR.SPINNING_GUN, CHAR.PUSHER, CHAR.LION, CHAR.TIGER, CHAR.QUESTION_MARK, CHAR.HEAD, CHAR.SEGMENT, CHAR.QUESTION_MARK, CHAR.FLOOR, CHAR.WATER_N, CHAR.WATER_S, CHAR.WATER_W, CHAR.WATER_E, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.ROTON, CHAR.DRAGON_PUP, CHAR.PAIRER, CHAR.SPIDER, CHAR.WEB, CHAR.STONE, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.QUESTION_MARK, CHAR.BULLET, CHAR.HORIZ_RAY, CHAR.VERT_RAY, CHAR.STAR];
        this.element_func = this.initialize_renderer_draw_functions();
        this.default_stat = {"x": 0, "y": 0, "step_x": 0, "step_y": 0, "cycle": 0, "param1": 0, "param2": 0, "param3": 0, "follow": -1, "leader": -1, "oop": ""};

        this.ctx = null;
    }

    initialize_renderer_draw_functions()
    {
        let element_func = Array(256).fill(this.basic_draw);
        // TODO: Add everything else that needs it

        element_func[0] = this.empty_draw;
        element_func[1] = this.edge_draw;
        element_func[3] = this.monitor_draw;
        element_func[12] = this.duplicator_draw;
        element_func[13] = this.bomb_draw;
        element_func[72] = this.star_draw;
        element_func[16] = this.conveyor_cw_draw;
        element_func[17] = this.conveyor_ccw_draw;
        element_func[28] = this.invisible_draw;
        element_func[30] = this.transporter_draw;
        element_func[31] = this.line_draw;
        element_func[36] = this.object_draw;
        element_func[39] = this.spinning_gun_draw;
        element_func[40] = this.pusher_draw;


        element_func[60] = this.dragon_pup_draw;
        element_func[63] = this.line_draw; // Webs use ElementConnected Draw
        element_func[64] = this.stone_draw;

        element_func.fill(this.text_draw, 73);

        return element_func;
    }

    dragon_pup_draw(x, y)
    {
        // TODO https://github.com/asiekierka/reconstruction-of-super-zzt/blob/master/SRC/ELEMENTS.PAS
        let element = this.rendered_board.elements[x][y];
        return [element.color % 16, parseInt(element.color / 16), 237];
    }

    get_line_chars(id)
    {
        if (id == 63) // Webs
            return [250, 179, 179, 179, 196, 217, 191, 180, 196, 192, 218, 195, 196, 193, 194, 197];
        return [249, 208, 210, 186, 181, 188, 187, 185, 198, 200, 201, 204, 205, 202, 203, 206];
    }

    stone_draw(x, y)
    {
        let char = 65 + Math.floor(Math.random() * 26);
        let fg = 9 + Math.floor(Math.random() * 7);
        let bg = 0;
        return [fg, bg, char];
    }

    text_draw(x, y)
    {
        let element = this.rendered_board.elements[x][y];
        if (element.id == 79) // White text gets black background instead of gray
            return [15, 0, element.color]
        return [15, (element.id - 72) % 16, element.color]; // mod 16 to handle undefined elements
    }

}
