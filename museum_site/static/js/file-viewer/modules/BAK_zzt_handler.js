import { Handler } from "./handler.js";
import { Character_Set } from "./character_set.js";
import { Palette } from "./palette.js";

export class ZZT_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "ZZT Handler";
        this.envelope_css_class = "zzt";
        this.world = {};
        this.boards = [];
        this.renderer = new ZZT_Standard_Renderer();
        this.DEBUG_BOARD_NUM = 8;
        this.show_border = true; // Show the board edges that surround a board

        this.max_flags = 10;
        this.tile_count = 1500; // TODO Should we use width * height of boards?
    }

    parse_bytes() {
        let start = Date.now();
        this.pos = 0;
        this.data = new DataView(this.bytes.buffer);

        // Parse World
        this.world = this.parse_world();
        this.boards = this.parse_boards();

        let fin = Date.now();
        console.log(`Bytes parsed in  ${fin - start}ms`);
    }

    async generate_html() {
        console.log("ZZT HTML Generation");

        /*
        let output = `<div style="flex:0 0 90%"><textarea style="width:90%;height:300px;">${JSON.stringify({"world": this.world, "boards": this.boards}, null, "\t")}</textarea>`;

        let temp = "";
        for (var idx = 0; idx < this.boards.length; idx++)
        {
            temp += this.boards[idx].title.debug() + "\n";
        }

        output += `<hr>${temp}</div>`
        */

        let output = await this.renderer.render_board(this.boards[this.DEBUG_BOARD_NUM]);
        console.log("THIS IS THE FINAL CONSOLE.LOG");
        return output;
    }

    read_keys()
    {
        // Record raw bytes corresponding to the 7 colored keys
        let output = [];
        for (let idx = 0; idx < 7; idx++)
        {
            output.push(this.read_Uint8());
        }
        return output;
    }

    read_flags()
    {
        // Record flag data
        let output = [];
        for (var idx = 0; idx < this.max_flags; idx++)
        {
            output.push(this.read_PString(20));
        }
    }

    read_unused(length)
    {
        // Read unused data
        let output = [];
        for (var idx = 0; idx < length; idx++)
        {
            output.push(this.read_Uint8());
        }
    }

    parse_world()
    {
        let world = {};
        world.identifier = this.read_Int16();
        world.total_boards = this.read_Int16();
        world.ammo = this.read_Int16();
        world.gems = this.read_Int16();
        world.keys = this.read_keys();
        world.health = this.read_Int16();
        world.current_board = this.read_Int16();
        world.torches = this.read_Int16();
        world.torch_ticks = this.read_Int16();
        world.energizer_ticks = this.read_Int16();
        world.unused = this.read_Int16();
        world.score = this.read_Int16();
        world.world_name = this.read_PString(20);
        world.flags = this.read_flags();
        world.board_time_seconds = this.read_Int16();
        world.board_time_hseconds = this.read_Int16(); // Hundredth-seconds
        world.is_save = this.read_Uint8();
        world.unused = this.read_unused(14);
        return world;
    }

    parse_boards()
    {
        // Parse boards
        let boards = [];
        this.pos = 512; // Start of board data in a world

        while (this.pos < this.bytes.length)
        {
            if (boards.length > this.world.total_boards) // Stop parsing beyond defined board count. TODO: What if you lie about this value and have more boards?
            {
                break;
            }
            let board = {
                "meta": {"board_address": this.pos, "element_address": this.pos + 53, "stats_address": this.pos + 53}
            };
            board.size = this.read_Int16();
            board.title = this.read_PString(50);

            // RLE
            board.elements = [];
            let read_tiles = 0;
            while (read_tiles < this.tile_count)
            {
                let quantity = this.read_Uint8();
                let element_id = this.read_Uint8();
                let color = this.read_Uint8();

                // RLE quantities of 0 are treated as 256. This is never relevant, but it's been documented and should be supported.
                if (quantity == 0)
                    quantity = 256;

                for (let quantity_idx = 0; quantity_idx < quantity; quantity_idx++)
                    board.elements.push({"id": element_id, "color": color});

                read_tiles += quantity;
                board.meta.stats_address += 3;

            }

            // Board properties
            board.max_shots = this.read_Uint8();
            board.is_dark = this.read_Uint8();
            board.neighbor_boards = [this.read_Uint8(), this.read_Uint8(), this.read_Uint8(), this.read_Uint8()];
            board.reenter_when_zapped = this.read_Uint8();
            board.message = this.read_PString(58);
            board.start_player_x = this.read_Uint8();
            board.start_player_y = this.read_Uint8();
            board.time_limit = this.read_Int16();
            board.unused = this.read_unused(16);
            board.stat_count = this.read_Int16();
            board.meta.stats_address += 88;

            // Stats
            board.stats = [];

            let read_stats = 0;
            while (read_stats < board.stat_count + 1)
            {
                let stat = {};
                stat.x = this.read_Uint8();
                stat.y = this.read_Uint8();
                stat.step_x = this.read_Int16();
                stat.step_y = this.read_Int16();
                stat.cycle = this.read_Int16();
                stat.param1 = this.read_Uint8();
                stat.param2 = this.read_Uint8();
                stat.param3 = this.read_Uint8();
                stat.follower = this.read_Int16();
                stat.leader = this.read_Int16();
                stat.under = { "element_id": this.read_Uint8(), "color": this.read_Uint8() };

                // Not properly implemented yet probs:
                stat.pointer = this.read_unused(4);
                stat.instruction = this.read_Int16();
                stat.oop_length = this.read_Int16();
                stat.padding = this.read_unused(8);
                if (stat.oop_length > 0)
                    stat.oop = this.read_Ascii(stat.oop_length);

                read_stats++;
                board.stats.push(stat);
            }

            // Jump to the start of the next board in file (for corrupt boards)
            let manual_pos = (board.meta.board_address + board.size) + 2;
            if ((this.pos != manual_pos))
            {
                board.meta.corrupt = true;
                this.pos = manual_pos;
            }

            // Add the finalizared parsed board to the list
            boards.push(board);
        }
        return boards
    }
}


class ZZT_Standard_Renderer
{
    constructor()
    {
        this.name = "ZZT Standard Renderer";
        this.board_width = 62; // Dimensions include the non-rendered border
        this.board_height = 27;
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
    }

    async render_board(board)
    {
        console.log("TOLD TO RENDER BOARD", board);
        if (! this.character_set.loaded)
            await this.character_set.load();
        this.active_board = board;

        console.log("Charset loaded, back in render board");

        console.log("Rendering a board");
        const canvas = document.createElement("canvas");
        canvas.setAttribute("width", `${(this.board_width - 2) * this.character_set.tile_width}px`); // -2 to remove border
        canvas.setAttribute("height", `${(this.board_height - 2) * this.character_set.tile_height}px`);
        canvas.setAttribute("style", "border:5px solid #000;");

        const ctx = canvas.getContext("2d");

        let element_idx = 0;
        for (var y = 1; y < 26; y++)
        {
            for (var x = 1; x < 61; x++)
            {
                let [fg, bg, char] = this.element_func[this.active_board.elements[element_idx].id].apply(this, [element_idx]);

                let ch_x = char % 16;
                let ch_y = parseInt(char / 16);

                // Background
                ctx.globalCompositeOperation = "source-over";
                ctx.fillStyle = bg;
                ctx.fillRect((x - 1) * this.character_set.tile_width, (y - 1) * this.character_set.tile_height, this.character_set.tile_width, this.character_set.tile_height);

                // Foreground transparency
                ctx.globalCompositeOperation = "xor";
                ctx.drawImage(
                    this.character_set.image, ch_x * this.character_set.tile_width, ch_y * this.character_set.tile_height, this.character_set.tile_width, this.character_set.tile_height,
                    (x - 1) * this.character_set.tile_width, (y - 1) * this.character_set.tile_height, this.character_set.tile_width, this.character_set.tile_height
                );

                // Foreground
                ctx.globalCompositeOperation = "destination-over";
                ctx.fillStyle = fg;
                ctx.fillRect((x - 1) * this.character_set.tile_width, (y - 1) * this.character_set.tile_height, this.character_set.tile_width, this.character_set.tile_height); // -1 for border compensation

                element_idx++;
            }
        }

        return canvas;
    }

    get_stats_for_element(element_idx, limit=1)
    {
        // Returns an array to support stat-stacking.
        let [x, y] = this.element_idx_to_coords(element_idx);
        let output = [];
        let matches = 0;
        for (let idx = 0; idx < this.active_board.stats.length; idx++)
        {
            if (this.active_board.stats[idx].x == x && this.active_board.stats[idx].y == y)
            {
                output.push(this.active_board.stats[idx])
                matches++;
            }
            if (matches >= limit)
                break;
        }

        if (output.length == 0) // This element is statless
        {
            console.log("STATLESS ELEMENT. TODO");
        }
        return output;
    }

    element_idx_to_coords(element_idx)
    {
        return [element_idx % 60 + 1, parseInt(element_idx / 60) + 1];
    }

    basic_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], this.default_characters[element.id]];
    }

    empty_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        return [this.palette.hex_colors[0], this.palette.hex_colors[0], this.default_characters[element.id]];
    }

    text_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        if (element.id == 53) // White text gets black background instead of gray
            return [this.palette.hex_colors[15], this.palette.hex_colors[0], element.color]
        return [this.palette.hex_colors[15], this.palette.hex_colors[(element.id - 46)], element.color]
    }

    pusher_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        let stat = this.get_stats_for_element(element_idx)[0];
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

    duplicator_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        let stat = this.get_stats_for_element(element_idx)[0];
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

    bomb_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        let stat = this.get_stats_for_element(element_idx)[0];
        let char;

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        if (stat.param1 <= 1)
            char = 11
        else
            char = (48 + stat.param1) % 256;

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    star_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        let stat = this.get_stats_for_element(element_idx)[0];
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

    conveyor_cw_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        let stat = this.get_stats_for_element(element_idx)[0];
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

    conveyor_ccw_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        let stat = this.get_stats_for_element(element_idx)[0];
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

    transporter_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        let stat = this.get_stats_for_element(element_idx)[0];
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

    line_draw(element_idx)
    {
        return this.basic_draw(element_idx);
    }

    object_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
        let stat = this.get_stats_for_element(element_idx)[0];
        let char = stat.param1;

        if (typeof stat == "undefined")
            return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], 63];

        return [this.palette.hex_colors[element.color % 16], this.palette.hex_colors[parseInt(element.color / 16) % 8], char];
    }

    spinning_gun_draw(element_idx)
    {
        let element = this.active_board.elements[element_idx];
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
