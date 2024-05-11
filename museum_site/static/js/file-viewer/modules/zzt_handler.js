import { Handler } from "./handler.js";
import { ZZT_Standard_Renderer } from "./renderer.js";

export class ZZT_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        console.log("WTF IS META HERE", meta);
        super(fvpk, filename, bytes, meta);
        this.name = "ZZT Handler";
        this.envelope_css_class = "zzt";
        this.world = {};
        this.boards = [];
        this.renderer = null;
        this.default_renderer = ZZT_Standard_Renderer;
        this.selected_board = null;

        this.max_flags = 10;
        this.tile_count = 1500; // TODO Should we use width * height of boards?

        this.cursor_tile = {"x": -1, "y": -1} // Tile the cursor was last seen over
    }

    static stat_list_label(stat, board)
    {
        let element = board.elements[stat.x][stat.y];
        let name = "Object";
        if (element.id == 36 && stat.oop[0] == "@") // TODO Magic Num
        {
            name = stat.oop.slice(0, stat.oop.indexOf("\n")) + ` ${stat.oop_length} bytes`;
        }
        else
        {
            name = "ELEMENT #" + element.id;
        }
        let output = `(${stat.x}, ${stat.y}) ${name}`;
        console.log(element);
        return output;
    }

    parse_bytes() {
        let start = Date.now();
        this.pos = 0;
        this.data = new DataView(this.bytes.buffer);

        // Parse World
        this.world = this.parse_world();
        this.boards = this.parse_boards();
        this.selected_board = this.world.current_board;

        let fin = Date.now();
        console.log(`Bytes parsed in  ${fin - start}ms`);
    }

    async generate_html() {
        console.log("ZZT HTML Generation");
        let board_idx = (this.selected_board !== null) ? this.selected_board : this.world.current_board;
        if (! this.renderer)
            this.renderer = new this.default_renderer();

        console.log("BOARD IDX IS", board_idx);

        let output = [
            {"target": this.envelope_id, "html": await this.renderer.render_board(this.boards[board_idx])},
            {"target": "#world-info", "html": this.get_world_info()},
            {"target": `.fv-content[data-fvpk="${this.fvpk}"]`, "html": this.display_board_list()},
            {"target": "#stat-info", "html": this.display_stat_list()},
            {"target": "#board-info", "html": this.get_board_info(), "focus": true},
        ];
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
        return output;
    }

    read_unused(length)
    {
        // Read unused data
        let output = [];
        for (var idx = 0; idx < length; idx++)
        {
            output.push(this.read_Uint8());
        }
        return output;
    }

    parse_world()
    {
        console.log("Parsing world");
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

            board.elements = Array(62).fill(0).map(x=> Array(27).fill(0)); // This is necessary

            // Create board border
            const edge = {"id": 1, "color": 1}; // TODO: Should be color 0
            for (let x = 0; x <= 61; x++)
            {
                board.elements[x][0] = edge;
                board.elements[x][26] = edge;
            }
            for (let y = 0; y <= 26; y++)
            {
                board.elements[0][y] = edge;
                board.elements[61][y] = edge;
            }

            // RLE
            let read_tiles = 0;
            let tile_idx = 0;
            while (read_tiles < this.tile_count)
            {
                let quantity = this.read_Uint8();
                let element_id = this.read_Uint8();
                let color = this.read_Uint8();

                // RLE quantities of 0 are treated as 256. This is never relevant, but it's been documented and should be supported.
                if (quantity == 0)
                    quantity = 256;

                for (let quantity_idx = 0; quantity_idx < quantity; quantity_idx++)
                {
                    let x = tile_idx % 60 + 1
                    let y = parseInt(tile_idx / 60) + 1;
                    board.elements[x][y] = {"id": element_id, "color": color};
                    tile_idx++;
                }

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
                stat.oop = "";
                if (stat.oop_length > 0)
                    stat.oop = this.read_Ascii(stat.oop_length).replace("♪", "\n");

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

            boards.push(board);  // Add the finalizared parsed board to the list
        }
        return boards
    }

    get_world_info()
    {
        let output = `<table>`;
        let rows = [
            {"value": this.world.identifier, "label": "Format", },
            {"value": this.world.world_name, "label": "Name"},
            {"value": this.world.current_board, "label": "Current Board", },
            {"value": this.world.total_boards, "label": "Total Boards", },
            {"value": this.world.health, "label": "Health", },
            {"value": this.world.ammo, "label": "Ammo", },
            {"value": this.world.torches, "label": "Torches", },
            {"value": this.world.gems, "label": "Gems", },
            {"value": this.world.keys, "label": "Keys", },
            {"value": this.world.score, "label": "Score", },
            {"value": this.world.torch_ticks, "label": "Torch Ticks", },
            {"value": this.world.energizer_ticks, "label": "Energizer Ticks", },
            {"value": `${this.world.board_time_seconds}.${this.world.board_time_hseconds}`, "label": "Board Time", },
            {"value": this.world.is_save, "label": "Is Save", },
            //{"value": this.world.unused, "label": "", },
            {"value": this.world.flags, "label": "Flags", },
        ];

        for (let i=0; i<rows.length; i++)
        {
            output += `<tr><th>${rows[i].label}</th><td>${rows[i].value}</td></tr>\n`;
        }
        output += `</table>`;

        return output;
    }

    get_board_info()
    {
        let board = this.boards[this.selected_board]
        let output = `<table>`;
        let rows = [
            {"value": board.title, "label": "Title:"},
            {"value": board.max_shots, "label": "Can Fire:"},
            {"value": board.is_dark, "label": "Board Is Dark:"},
            {"value": board.reenter_when_zapped, "label": "Re-enter When Zapped:"},
            {"value": `(${board.start_player_x}, ${board.start_player_y})`, "label": "Re-enter X/Y:"},
            {"value": board.time_limit, "label": "Time Limit:"},
            {"value": `${board.stat_count} / 151`, "label": "Stat Count:"},
            {"value": `${board.size} bytes`, "label": "Board Size:"},
            {"value": board.message, "label": "Message:"},
        ];

        for (let i=0; i<rows.length; i++)
        {
            output += `<tr><th>${rows[i].label}</th><td>${rows[i].value}</td></tr>\n`;
        }

        output += `<tr><th colspan="2">Board Exits</th></tr>`;
        rows = [
            {"value": board.neighbor_boards[0], "label": "↑:"},
            {"value": board.neighbor_boards[1], "label": "↓:"},
            {"value": board.neighbor_boards[2], "label": "←:"},
            {"value": board.neighbor_boards[3], "label": "→:"},
        ]

        for (let i=0; i<rows.length; i++)
        {
            output += `<tr><th>${rows[i].label}</th><td>${rows[i].value}</td></tr>\n`;
        }

        output += `</table>`;
        return output;
    }

    display_board_list()
    {
        console.log("WRITING BOARD LIST");
        let output = `${this.filename}<ol class='board-list' start='0' data-fv_func='board_change'>\n`;
        for (var idx = 0; idx < this.boards.length; idx++)
        {
            let chk_selected = (idx == this.selected_board) ? " selected" : "";
            output += `<li class='board${chk_selected}' data-board-number=${idx}>` + this.boards[idx].title.revealed_string() + "</li>\n";
        }
        output += "</ol>\n";

        return output;
    }

    display_stat_list()
    {
        console.log("WRITING SAT LIST");
        let output = `${this.filename}<ol class='stat-list' start='0' data-fv_func='stat-select'>\n`;
        for (var idx = 0; idx < this.boards[this.selected_board].stats.length; idx++)
        {
            let stat_label = ZZT_Handler.stat_list_label(this.boards[this.selected_board].stats[idx], this.boards[this.selected_board]);
            output += `<li>${stat_label}</li>`;
        }
        output += "</ol>\n";

        return output;
    }

    display_json_string()
    {
        let output = `<pre style='max-width:80ch;max-height:25ch;overflow:auto;border:1px solid #000;'>${JSON.stringify({"world": this.world, "boards": this.boards}, null, "\t")}</pre>`;
        return output;
    }

    mousemove(e)
    {
        let tile_x = Math.abs(parseInt(e.base_x / this.renderer.character_set.tile_width)) + 1;
        let tile_y = Math.abs(parseInt(e.base_y / this.renderer.character_set.tile_height)) + 1;

        if ((tile_x == this.cursor_tile.x) && (tile_y == this.cursor_tile.y) || (tile_x > 60 || tile_y > 25)) // TODO THESE NUMBERS SHOULD BE VARS
            return false;

        this.cursor_tile.x = tile_x;
        this.cursor_tile.y = tile_y;

        console.log(tile_x, tile_y);
    }
}
