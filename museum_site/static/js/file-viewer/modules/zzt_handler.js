import { padded, escape_html} from "./core.js"; // PString needed for watermark reading directly
import { Handler } from "./handler.js";
import { ZZT_Standard_Renderer, ZZT_Object_Highlight_Renderer, ZZT_Code_Highlight_Renderer, ZZT_Fake_Wall_Highlight_Renderer, SZZT_Standard_Renderer } from "./renderer.js";
import { ZZT_ELEMENTS, SZZT_ELEMENTS } from "./elements.js";

let ALT_BOARD_TITLES = ["Apple", "Bee", "Cat", "Dog", "Engine", "Fish", "Gum", "Horn", "Insect", "Jet", "King", "Lollipop", "Monkey", "Nose", "Octopus", "Pizza", "Queen", "Rocket", "Snake", "Toy", "Umbrella", "Vase", "Wagon", "X-Ray", "Yo-yo", "Zipper"];
let ALT_BOARD_PREFIXES = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa"];

while (ZZT_ELEMENTS.length < 256)
{
    ZZT_ELEMENTS.push({"id":ZZT_ELEMENTS.length, "name":`<i>Undefined Element ${ZZT_ELEMENTS.length}</i> `, "oop_name":"", "character":63})
}

while (SZZT_ELEMENTS.length < 256)
{
    SZZT_ELEMENTS.push({"id":SZZT_ELEMENTS.length, "name":`<i>Undefined Element ${SZZT_ELEMENTS.length}</i> `, "oop_name":"", "character":63})
}

export class ZZT_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "ZZT Handler";
        this.envelope_css_class = "zzt";
        this.initial_content = `<div class="inner-envelope-wrapper"><canvas class="fv-canvas" data-foo="BAR"></canvas><div class="hover-wrapper"><div class="hover-element" style="display:none"></div></div><div class="crosshair-wrapper"><div class="crosshair"></div></div></div>`;
        this.showing_search_results = false;
        this.query = "";
        this.world = {};
        this.boards = [];
        this.default_renderer = ZZT_Standard_Renderer;
        this.renderer = new this.default_renderer(this.fvpk);
        this.selected_board = null;
        this.auto_click = ""; // Coordinates to pre-click an element when loading

        this.color_names = [
            "Black", "Dark Blue", "Dark Green", "Dark Cyan", "Dark Red", "Dark Purple", "Dark Yellow", "Gray",
            "Dark Gray", "Blue", "Green", "Cyan", "Red", "Purple", "Yellow", "White"
        ];

        this.first_board_start_idx = 512;
        this.board_name_length = 50;
        this.max_flags = 10;
        this.max_stats = 150;
        this.board_width = 60;
        this.board_height = 25;
        this.tile_count = 1500; // TODO Should we use width * height of boards?

        this.cursor_tile = {"x": -1, "y": -1} // Tile the cursor was last seen over

        this.tabs = [
            {"name": "world-info", "text": "World", "shortcut":"W"},
            {"name": "board-info", "text": "Board", "shortcut":"B"},
            {"name": "element-info", "text": "Element", "shortcut":"E"},
            {"name": "stat-info", "text": "Stats", "shortcut":"S"},
            {"name": "preferences", "text": "Prefs.", "shortcut":"P"},
            {"name": "help", "text":"?"},
        ];
        this.default_tab = "board-info";

        this.config_fields = [
            {"label_text": "Leftover Data", "widget": "select", "help_text": "Show full contents of certain strings regardless of specified length.", "config_setting": "pstrings.show_leftover_data", "data_type": "int", "options_data": [
                {"value": 0, "text": "Hide", "default": true},
                {"value": 1, "text": "Show", "default": false},
            ]},
            {"label_text": "Limit Stat Parsing", "widget": "select", "help_text": "Speed up parsing of corrupt boards by limiting the stats parsed to the engine's stat limit. No effect on non-corrupt boards. Fully parsing corrupt boards may cause file viewer to become unresponsive.", "config_setting": "corrupt.enforce_stat_limit", "data_type": "int", "options_data": [
                {"value": 1, "text": "Limit", "default": true},
                {"value": 0, "text": "Do Not Limit", "default": false},
            ]},
            {"label_text": "Zoom", "widget": "select", "help_text": "Scale rendered board to this size.", "config_setting": "display.zoom", "data_type": "int", "options_data": [
                {"value": 1, "text": "1x", "default": true},
                {"value": 2, "text": "2x", "default": false},
            ]},
            {"label_text": "OOP Style", "widget": "select", "help_text": "Display ZZT-OOP as modern syntax highlighted code or classic ZZT v3.2 style.", "config_setting": "oop.style", "data_type": "str", "options_data": [
                {"value": "modern", "text": "Modern", "default": true},
                {"value": "classic", "text": "Classic", "default": false},
            ]},
            {"label_text": "Rendering Method", "widget": "select", "help_text": "Choose how to translate board data into a rendered image.", "config_setting": "rendering_method.name", "data_type": "str", "options_data": [
                {"value": "ZZT Standard Renderer", "text": "ZZT - Standard", "default": true},
                {"value": "ZZT Object Highlight Renderer", "text": "ZZT - Object Highlight", "default": false},
                {"value": "ZZT Code Highlight Renderer", "text": "ZZT - Code Highlight", "default": false},
                {"value": "ZZT Fake Wall Highlight Renderer", "text": "ZZT - Fake Wall Highlight", "default": false},
            ]},
        ];
    }

    static initial_config = {
        "pstrings": {
            "show_leftover_data": 0,
        },
        "stats": {
            "sort": "name",
            "show_codeless": 1,
        },
        "corrupt": {
            "enforce_stat_limit": 1,
        },
        "display": {
            "zoom": 1,
        },
        "oop": {
            "style": "modern",
        },
        "rendering_method": {
            "name": "ZZT_Standard_Renderer",
        },
    }

    static stat_list_label(stat, board)
    {
        let element, name;
        try {
            element = board.elements[stat.x][stat.y];
            name = ZZT_Handler.element_lookup(element.id).name;
        }
        catch (error)
        {
            console.log("ERROR IS", error);
            name = "<i>Out of Bounds Stat</i>";
        }
        if (stat.oop[0] == "@")
        {
            name = escape_html(stat.oop.slice(0, stat.oop.indexOf("\n")));
        }
        let byte_count = (stat.oop != "") ? ` ${stat.oop_length} bytes` : '';
        let output = `<a class="stat-link jsLink" data-x="${stat.x}" data-y="${stat.y}">(${padded(stat.x)}, ${padded(stat.y)}) ${name}</a>${byte_count}`;
        return output;
    }

    static element_lookup(idx) { return ZZT_ELEMENTS[idx]; }
    call_element_lookup(idx) { return ZZT_Handler.element_lookup(idx); }

    parse_bytes() {
        let start = Date.now();
        this.pos = 0;
        this.data = new DataView(this.bytes.buffer);

        // Parse File
        this.world = this.parse_world();
        this.boards = this.parse_boards();
        this.locks = this.parse_locks();

        if (this.selected_board === null)
            this.selected_board = this.world.current_board;

        let fin = Date.now();
        console.log(`${this.filename} - ${this.data.byteLength} bytes parsed in ${fin - start}ms`);
    }

    async write_html() {
        let BLANK_TARGET = {"target": null, "html": ""};
        if ((! this.renderer) || (this.renderer.name != this.config.rendering_method.name.replaceAll("_", " ")))
        {
            console.log("Changing Renderer!");
            console.log("Current name:", this.renderer.name, " New:", this.config.rendering_method.name);
            this.renderer = this.get_renderer_object_from_config();
        }

        await this.display_board_canvas();

        let targets = [
            {"target": ".hover-element", "html": ""},
            {"target": "#world-info", "html": this.get_world_tab()},
            ((this.showing_search_results) ? BLANK_TARGET : {"target": `.fv-content[data-fvpk="${this.fvpk}"]`, "html": this.write_board_list()}),
            {"target": "#element-info", "html": "<i>No element selected. Click on a tile to view its defails.</i>"},
            {"target": "#stat-info", "html": this.write_stat_list()},
            {"target": "#board-info", "html": this.get_board_info(),},
            //{"target": "#fv-main", "html": "<textarea style='width:700px;height:500px;'>" +this.display_json_string() + "</textarea>",},
            {"target": "#preferences", "html": this.get_preferences(),},
        ];

        if (this.showing_search_results)
        {
            $(`.board.selected`).removeClass("selected");
            $(`.board[data-board-number=${this.selected_board}]`).addClass("selected");
        }

        this.write_targets(targets);

        /* Manually size the canvas */
        console.log("Does this envelope exist yet?", $(".envelope-zzt.active"));
        if (this.config.display.zoom == 1)
        {
            $(".envelope-zzt").css("min-height", "");
        }
        else
        {
            let new_height = $(".fv-canvas").attr("height").slice(0, -2);
            console.log("NEW HEIGHT", new_height);
            console.log("CSS Val", (new_height * this.config.display.zoom) + "px");
            $(".envelope-zzt").css("min-height",  (new_height * this.config.display.zoom + 20) + "px"); // + 20 pixels for border (as it's doubled now...) + 5 for ugh why are you still scrolling
        }

        console.log("AUTO CLICK COORDS:", this.auto_click);
        if (this.auto_click)
        {
            let coords = this.auto_click.replace("#", "").split(",");
            this.auto_click = "";
            this.write_element_info(parseInt(coords[0]), parseInt(coords[1]));
        }
        else
        {
            this.display_tab(this.default_tab);
        }

        //$(window).scrollTop($("#fv-main").offset().top);
        return true;
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
        world.watermark = this.read_Ascii(232).replace(/\u0000/g, "");
        return world;
    }

    initialize_empty_board()
    {
        let board = {
            "meta": {"board_address": this.pos, "element_address": this.pos + 53, "stats_address": this.pos + 53} // TODO IS THIS USED AT ALL
        };
        board.size = this.read_Int16();
        board.title = this.read_PString(this.board_name_length);
        board.elements = Array(this.board_width + 2).fill(0).map(x=> Array(this.board_height + 2).fill(0)); // Empty board with border.

        // Create board border
        const edge = {"id": 1, "color": 0};
        for (let x = 0; x <= (this.board_width + 1); x++)
        {
            board.elements[x][0] = edge;
            board.elements[x][this.board_height + 1] = edge;
        }
        for (let y = 0; y <= (this.board_height + 1); y++)
        {
            board.elements[0][y] = edge;
            board.elements[this.board_width + 1][y] = edge;
        }
        return board;
    }

    read_board_rle(board)
    {
        let read_tiles = 0;
        let tile_idx = 0;
        while (read_tiles < this.tile_count)
        {
            let quantity = this.read_Uint8();
            let element_id = this.read_Uint8();
            let color = this.read_Uint8();

            // RLE quantities of 0 are treated as 256. This is never relevant, but it's been documented and should be supported.
            if (quantity == 0) { quantity = 256 };

            for (let quantity_idx = 0; quantity_idx < quantity; quantity_idx++)
            {
                let x = tile_idx % this.board_width + 1
                let y = parseInt(tile_idx / this.board_width) + 1;
                board.elements[x][y] = {"id": element_id, "color": color};
                tile_idx++;
            }

            read_tiles += quantity;
            board.meta.stats_address += 3;
        }
        return board;
    }

    read_board_properties(board)
    {
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
        return board;
    }

    read_board_stats(board)
    {
        board.stats = [];

        let read_stats = 0;
        let stat_cutoff = (this.config.corrupt.enforce_stat_limit) ? Math.min(board.stat_count, this.max_stats) : board.stat_count;
        while (read_stats < stat_cutoff + 1)
        {
            let stat = {};
            stat.idx = read_stats;
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
            stat.pointer = this.read_unused(4);
            stat.instruction = this.read_Int16();
            stat.oop_length = this.read_Int16();
            if (this.name == "ZZT Handler") // Only difference between ZZT/SZZT is this padding
                stat.padding = this.read_unused(8);
            stat.oop = "";
            if (stat.oop_length > 0)
                stat.oop = this.read_Ascii(stat.oop_length).replaceAll("♪", "\n");

            read_stats++;
            board.stats.push(stat);
        }
        return board;
    }

    parse_boards()
    {
        // Parse boards
        let boards = [];
        this.pos = this.first_board_start_idx; // Start of board data in a world

        while (this.pos < this.bytes.length)
        {
            let board;
            // TODO: What if you lie about this value and have more boards?
            if (boards.length > this.world.total_boards) // Stop parsing beyond defined board count.
            {
                break;
            }
            board = this.initialize_empty_board();
            board = this.read_board_rle(board);
            board = this.read_board_properties(board);
            board = this.read_board_stats(board);

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

    parse_locks()
    {
        let locks = [];

        // Regular Lock
        for (let idx in this.world.flags)
        {
            if (this.world.flags[idx].toString().toUpperCase() == "SECRET")
                locks.push("Regular Lock");
        }

        // Super Lock
        if (this.boards[this.world.total_boards] && this.boards[this.world.total_boards].size == 4)
            locks.push("Super Lock");

        // Save Lock
        // TODO FIND A TEST WORLD
        if (this.world.is_save)
            locks.push("Save Lock");
        return locks;
    }

    get_world_info()
    {
        let output = `<div class="flex-table">`;
        let rows = [
            {"value": this.get_world_identifier(this.world.identifier), "label": "Format", },
            {"value": this.world.world_name, "label": "Name"},
            {"value": this.board_link(this.world.current_board), "label": "Starting Board", },
            {"value": this.world.total_boards, "label": "Total Boards", },
            {"value": this.world.health, "label": "Health", },
            {"value": this.world.ammo, "label": "Ammo", },
            {"value": this.world.torches, "label": "Torches", },
            {"value": this.world.gems, "label": "Gems", },
            {"value": this.get_keys_value(), "label": "Keys", },
            {"value": this.world.score, "label": "Score", },
            {"value": this.world.torch_ticks, "label": "Torch Ticks", },
            {"value": this.world.energizer_ticks, "label": "Energizer Ticks", },
            {"value": `${this.world.board_time_seconds}.${this.world.board_time_hseconds}`, "label": "Board Time", },
            {"value": this.yesno(this.world.is_save), "label": "Is Save", },
            //{"value": this.world.unused, "label": "", },
            {"value": this.get_flags_value(), "label": "Flags", },
            {"value": this.get_locks_value(), "label": "Detected Locks", },
        ];

        if (this.world.watermark)
        {
            rows.push({"value": this.world.watermark, "label": "Watermark"});
        }

        for (let i=0; i<rows.length; i++)
        {
            output += `<div class="flex-row"><div class="label">${rows[i].label}</div><div class="value">${rows[i].value}</div></div>\n`;
        }
        output += `</div>`;

        return output;
    }

    get_world_tab()
    {
        let output = this.get_world_info();

        output += `<div class="flex-table">\n`;

        output += `<div class="flex-row"><div class="label">ZZT-OOP Search</div><div class="value code-search-form"><input name="code-search" placeholder="#set frontkey" value="${this.query}"><input type="button" value="Search" name="code-search-button"><input type="button" name="clear-search" value="Clear Search"><div class="code-search-no-results-message">&nbsp;</div></div></div>\n`;

        output += `<div class="flex-row"><div class="label">Misc. Tools (Experimental)</div><div class="value"><ul class="misc-tool-list"><li><a class="jsLink" data-tool="disambiguate_board_titles">Disambiguate Board Titles</a></li></ul></div></div>\n`;

        output += `</div>\n`;

        return output;
    }

    get_board_info()
    {
        let board = this.boards[this.selected_board]

        if (! board)
            return "<i>This file could not be parsed.</i>";

        let output = `<div class="flex-table">`;
        let rows = this.get_board_info_rows(board);

        for (let i=0; i<rows.length; i++)
        {
            output += `<div class="flex-row"><div class="label">${rows[i].label}</div><div class="value">${rows[i].value}</div></div>\n`;
        }

        output += `<div class="flex-row"><div class="label c">Board Exits</div></div>\n`;
        rows = [
            {"value": this.board_link(board.neighbor_boards[0], "north"), "label": "↑"},
            {"value": this.board_link(board.neighbor_boards[1], "south"), "label": "↓"},
            {"value": this.board_link(board.neighbor_boards[2], "west"), "label": "←"},
            {"value": this.board_link(board.neighbor_boards[3], "east"), "label": "→"},
        ]

        for (let i=0; i<rows.length; i+=2)
        {
            output += `<div class="flex-row">
                <div class="label c tiny">${rows[i].label}</div><div class="value">${rows[i].value}</div>
                <div class="label c tiny">${rows[i+1].label}</div><div class="value">${rows[i+1].value}</div>
            </div>\n`;
        }

        output += `</div>`;


        output += this.get_zeta_live();

        return output;
    }

    get_board_info_rows(board)
    {
        let rows = [
            {"value": board.title.toString(), "label": "Title"}, // TODO: Should this respect show hidden data?
            {"value": `${board.max_shots} shots.`, "label": "Can Fire"},
            {"value": this.yesno(board.is_dark), "label": "Board Is Dark"},
            {"value": this.yesno(board.reenter_when_zapped), "label": "Re-enter When Zapped"},
            {"value": `${this.coords_span(board.start_player_x, board.start_player_y)}`, "label": "Re-enter X/Y"},
            {"value": this.val_or_none(board.time_limit), "label": "Time Limit"},
            {"value": `${board.stat_count + 1} / ${this.max_stats + 1}`, "label": "Stat Count"},
            {"value": `${board.size} bytes`, "label": "Board Size"},
            {"value": (board.message.length ? board.message : "<i>None</i>"), "label": "Message"},
        ];
        return rows;
    }

    write_board_list()
    {
        console.log("WRITING BOARD LIST");
        let output = `${this.filename}<ol class='board-list' start='0' data-fv_func='board_change'>\n`;
        let func = (this.config.pstrings.show_leftover_data) ? "revealed_string" : "toString";
        for (var idx = 0; idx < this.boards.length; idx++)
        {
            let chk_selected = (idx == this.selected_board) ? " selected" : "";
            let board_title = this.boards[idx].title[func]();
            if (board_title == "")
                board_title = "<i>Untitled Board</i>";
            output += `<li class='board${chk_selected}' data-board-number=${idx}>` + board_title + "</li>\n";
        }
        output += "</ol>\n";

        return output;
    }

    write_stat_list()
    {
        let current_sort = this.config.stats.sort;
        let codeless = this.config.stats.show_codeless;
        console.log("Current sort", current_sort);
        console.log("codeless?", codeless);
        let sort_funcs = {
            "sort_stat_list_by_code": this.sort_stat_list_by_code,
            "sort_stat_list_by_coords": this.sort_stat_list_by_coords,
            "sort_stat_list_by_name": this.sort_stat_list_by_name,
            "sort_stat_list_by_index": this.sort_stat_list_by_index,
        }
        let sorted_stat_list = this[`sort_stat_list_by_${current_sort}`]();
        let output = `<div class="controls">
            <label>Sort by: <select name="stat-sort">
                <option value="code"${(current_sort == 'code') ? ' selected' : ''}>Code Length</option>
                <option value="coords"${(current_sort == 'coords') ? ' selected' : ''}>Coordinates</option>
                <option value="name"${(current_sort == 'name') ? ' selected' : ''}>Name</option>
                <option value="index"${(current_sort == 'index') ? ' selected' : ''}>Stat Index</option>
            </select></label>
            <label>Show stats without code: <input type="checkbox" name="show-codeless" ${codeless ? ' checked' : ''}></label>
        </div>`;
        output += `<ol class='stat-list' start='0' data-fv_func='stat-select'>\n`;

        for (var idx = 0; idx < sorted_stat_list.length; idx++)
        {
            let hidden = "";
            let stat_label;
            //console.log("Stat oop is?", sorted_stat_list[idx].oop.slice(0,15));
            if (! codeless && sorted_stat_list[idx].oop == "")
                hidden = " class='none'";
            if (this.name == "ZZT Handler")
                stat_label = ZZT_Handler.stat_list_label(sorted_stat_list[idx], this.boards[this.selected_board]);
            else if (this.name == "Super ZZT Handler")
                stat_label = SZZT_Handler.stat_list_label(sorted_stat_list[idx], this.boards[this.selected_board]);

            output += `<li${hidden} value="${sorted_stat_list[idx].idx}">${stat_label}</li>`;
        }
        output += "</ol>\n";

        return output;
    }

    display_json_string()
    {
        // TODO Needs to be implemented to actually display this and request it.
        let output = `<pre style='max-width:80ch;max-height:25ch;overflow:auto;border:1px solid #000;'>${JSON.stringify({"world": this.world, "boards": this.boards}, null, "\t")}</pre>`;
        return output;
    }

    async display_board_canvas()
    {
        console.log("FUNC DISPLAY_BOARD_CANVAS", this.fvpk);
        let board_idx = (this.selected_board !== null) ? this.selected_board : this.world.current_board;
        let canvas = await this.renderer.render_board(this.boards[board_idx], this.config.display.zoom);
        return true;
    }

    mousemove(e)
    {
        if ((e.x < 0 || e.y < 0)) // TODO: Needs to cut off lower and right borders as well
        {
            this.mouseout(e);
            this.cursor_tile.x = -1;
            this.cursor_tile.y = -1;
            return false
        }
        let coords = this.get_tile_coordinates_from_cursor_position(e);

        if ((coords.x == this.cursor_tile.x) && (coords.y == this.cursor_tile.y) || (coords.x > this.board_width || coords.y > this.board_height || coords.x < 0 || coords.y < 0))
            return false;

        this.cursor_tile.x = coords.x;
        this.cursor_tile.y = coords.y;

        let element_id = this.boards[this.selected_board].elements[coords.x][coords.y].id;
        let color_id = this.boards[this.selected_board].elements[coords.x][coords.y].color;
        let element = this.call_element_lookup(element_id);

        // Sizing
        $(".hover-element").removeClass(`zoom-2`); // TODO This assumes only 1x and 2x zooms
        if (this.config.display.zoom != 1)
            $(".hover-element").addClass(`zoom-${this.config.display.zoom}`);

        // Color
        let fg = color_id % 16;
        let bg = parseInt(color_id / 16);
        let bg_x = parseInt(fg * -8);
        let bg_y = parseInt(bg * -14);
        $(".hover-element").html(`(${padded(coords.x)}, ${padded(coords.y)})<br><div class='color-swatch' style='background-position: ${bg_x}px ${bg_y}px'></div> ${element.name}`);


        // Positioning
        if (coords.y < 7)
            $(".hover-element").addClass("bottom");
        else if (coords.y > 20)
            $(".hover-element").removeClass("bottom");

        $(".hover-element").show();
    }

    mouseout(e)
    {
        $(".hover-element").hide();
        this.cursor_tile.x = -1;
        this.cursor_tile.y = -1;
    }

    get_tile_coordinates_from_cursor_position(e)
    {
        let scale = this.config.display.zoom;
        let output = {
            "x": Math.abs(parseInt((e.x) / (this.renderer.character_set.tile_width * scale))) + 1,
            "y": Math.abs(parseInt((e.y) / (this.renderer.character_set.tile_height * scale))) + 1,
        }
        return output;
    }

    canvas_click(e)
    {
        const coords = this.get_tile_coordinates_from_cursor_position(e);
        history.replaceState(undefined, undefined, `#${coords.x},${coords.y}`);
        return this.write_element_info(coords.x, coords.y);
    }

    canvas_double_click(e)
    {
        const coords = this.get_tile_coordinates_from_cursor_position(e);
        let element_id = this.boards[this.selected_board].elements[coords.x][coords.y].id;
        if (element_id != 11) // TODO: Magic Number for Passage ID
            return false;

        let destination_board_num = -1;
        for (var idx = 0; idx < this.boards[this.selected_board].stats.length; idx++)
        {
            let stat = this.boards[this.selected_board].stats[idx]
            if (stat.x == coords.x && stat.y == coords.y)
            {
                destination_board_num = stat.param3;
                break
            }
        }

        if (destination_board_num == -1 || destination_board_num > this.world.total_boards)
            return false;

        this.selected_board = destination_board_num;
        this.render();
    }

    write_element_info(x, y)
    {
        let element_id, color_id, element;
        try
        {
            element_id = this.boards[this.selected_board].elements[x][y].id;
            color_id = this.boards[this.selected_board].elements[x][y].color;
            element = this.call_element_lookup(element_id);
        }
        catch (error)
        {
            // Use a fictionalized OOB elements
            element = {
                "id":"<i>None</i>",
                "name":"<i>Out of Bounds Element</i>",
                "oop_name":"",
                "character":63
            }
        }
        let output = `<table>`;

        let rows = [
            {"value": `${this.coords_span(x, y)}`, "label": "Position", },
            {"value": element.name, "label": "Name", },
            {"value": element.id, "label": "ID", },
            {"value": this.get_color(color_id), "label": "Color", },
        ];

        let tile_stats = this.get_all_stats_for_tile(x, y)
        let oop_html = this.write_zzt_oop(tile_stats);
        let first_column = true;

        for (let idx=0; idx<tile_stats.length; idx++)
        {
            let stat_info = [
                {"value": `${tile_stats[idx].param1}`, "label": `${this.get_param_name_for_element(element.id, 1)}`, },
                {"value": `${tile_stats[idx].cycle}`, "label": "Cycle", },
                {"value": `${this.get_param2_value(element.id, tile_stats[idx].param2)}`, "label": `${this.get_param_name_for_element(element.id, 2)}`, },
                {"value": `${this.call_element_lookup(tile_stats[idx].under.element_id).name}`, "label": "Under Element", },
                {"value": `${this.get_param3_value(element.id, tile_stats[idx].param3)}`, "label": `${this.get_param_name_for_element(element.id, 3)}`, },
                {"value": `${this.get_color(tile_stats[idx].under.color)}`, "label": "Under Color", },
                {"value": `${this.get_step(tile_stats[idx])}`, "label": "Step (X, Y)", },
                {"value": `${this.get_bound_stat(tile_stats[idx])}`, "label": "Bound to", },
                {"value": `${this.get_leader_follower_value(tile_stats[idx].leader)}`, "label": "Leader", },
                {"value": `${this.get_leader_follower_value(tile_stats[idx].follower)}`, "label": "Follower", },
                {"value": `${tile_stats[idx].oop_length}`, "label": "OOP Length", },
                {"value": `${tile_stats[idx].instruction}`, "label": "Instruction", },
                {"value": `${oop_html[idx]}`, "label": "Code", "row_template": "code"},
            ]
            rows = rows.concat(stat_info);
        }

        for (let i=0; i<rows.length; i++)
        {


            // TODO - This block should be organized and not so if/else-y? Maybe
            if (rows[i].row_template == "code")
            {
                output += `<tr><th colspan="4">${rows[i].label}</th></tr><tr><td colspan="4">${rows[i].value}</td>\n</tr>\n`;
                first_column = false; // Reset to first column for next datum
            }
            else
            {
                if (first_column)
                    output += `<tr>\n`;
                output += `<th>${rows[i].label}</th><td>${rows[i].value}</td>\n`;

                if (! first_column)
                    output += `</tr>\n`;
            }

            first_column = ! first_column;
        }

        output += `</table>`;


        $("#element-info").html(output);
        this.display_tab("element-info");
    }

    get_all_stats_for_tile(x, y)
    {
        let stat_list = [];
        for (var idx = 0; idx < this.boards[this.selected_board].stats.length; idx++)
        {
            let stat = this.boards[this.selected_board].stats[idx]
            if (stat.x == x && stat.y == y)
                stat_list.push(stat);
        }
        return stat_list
    }

    get_leader_follower_value(input)
    {
        return (input == -1) ? "<i>None</i>" : input;
    }

    get_param_name_for_element(element_id, param)
    {
        let default_param = "Param" + param;

        if (element_id == "<i>None</i>")
            return default_param

        if (this.call_element_lookup(element_id)["param" + param])
            return this.call_element_lookup(element_id)["param" + param];
        return default_param
    }

    get_param2_value(element_id, raw)
    {
        if (element_id == 39 || element_id == 42) // TODO MAGIC NUMBER
            return (raw >= 128) ? `${raw - 128} [Stars] (Raw: ${raw})` : `${raw} [Bullets]`;
        return raw;
    }

    get_param3_value(element_id, raw)
    {
        console.log("P3 for element id?", element_id);
        if (element_id == 11) // TODO MAGIC NUMBER
            return this.board_link(raw);
        return raw;
    }

    get_world_identifier()
    {
        let default_identifier = "<i>Unknown World Format</i>";
        let identifiers = {"-1": "ZZT", "-2": "Super ZZT"};
        return identifiers["" + this.world.identifier] || default_identifier;
    }

    board_link(board_num, direction="")
    {
        if (board_num)
        {
            if (board_num < 0 || board_num >= this.boards.length)
                return `<i>Corrupt Board Link</i>`;
            return `<a class="jsLink board-link" data-board-number="${board_num}" data-direction="${direction}">${padded(board_num)}. ${this.get_hr_title(board_num)}</a>`;
        }
        return `<i>None</i>`;
    }

    get_hr_title(board_num)
    {
        return (this.boards[board_num].title == "") ? "<i>Untitled Board</i>" : this.boards[board_num].title.toString(); // Force no errata
    }

    get_keys_value()
    {
        let colors = ["blue", "green", "cyan", "red", "purple", "yellow", "white"];
        let bg_colors = ["darkblue", "darkgreen", "darkcyan", "darkred", "darkpurple", "darkyellow", "gray"];
        let output = "";
        let has_keys = false
        for (var idx = 0; idx < this.world.keys.length; idx++)
        {
            let fg = colors[idx]
            let bg = bg_colors[idx];
            if (this.world.keys[idx] != 0)
            {
                has_keys = true;
                output += `<span class="cp437 ega-${fg} ega-${bg}-bg">♀</span>`;
            }
            else
                output += "<span class='cp437'>&nbsp;</span>"
        }
        if (! has_keys)
            output = "<i>None</i>";
        return output
    }

    get_flags_value()
    {
        let has_flags = false;

        let output = "<ol>\n";
        for (var idx = 0; idx < this.world.flags.length; idx++)
        {
            if (this.world.flags[idx].length)
            {
                has_flags = true;
                output += `<li>${this.world.flags[idx].toString()}</li>\n`; // TODO: Does not respect hidden data visibility settings
            }
        }
        if (! has_flags)
            output = "<i>None</i>";
        else
            output += "</ol>\n";
        return output;
    }

    get_locks_value()
    {
        let has_locks = false;
        let output = "<ul>\n";
        for (var idx = 0; idx < this.locks.length; idx++)
        {
            if (this.locks[idx].length)
            {
                has_locks = true;
                output += `<li>${this.locks[idx]}</li>\n`;
            }
        }
        if (! has_locks)
            output = "<i>None</i>";
        else
            output += "</ul>\n";
        return output;
    }

    yesno(val, yes="Yes", no="No")
    {
        return (val) ? yes : no;
    }

    val_or_none(val, none="<i>None</i>")
    {
        return (val) ? val : none;
    }

    write_zzt_oop(stats)
    {
        let output = [];
        // Takes a list of stat items and displays their CODE if any exists
        for (let idx=0; idx<stats.length; idx++)
        {
            let stat = stats[idx];
            if (! stat.oop)
                output.push("<i>None</i>");
            else
                output.push(`<details open><summary class="oop-summary"> ZZT-OOP</summary>
                ${this.render_zzt_oop_style(stat.oop)}</details>`);
        }
        return output;
    }

    render_zzt_oop_style(oop)
    {
        let rendered;
        oop = escape_html(oop);

        if (this.config.oop.style == "classic")
        {
            // TODO: Inline style should be moved. These classes are used in {% scroll %} though and may have an impact. */

            rendered = `<div class="zzt-scroll"><div class="name">Edit Program</div>\n<div class="content" style="white-space:pre">  •    •    •    •    •    •    •    •    •\n${oop}  •    •    •    •    •    •    •    •    •\n</div></div>`;
        }
        else
            rendered = `<code class="zzt-oop">` + this.syntax_highlight(oop) + `</code>`;

        return rendered
    }

    syntax_highlight(oop)
    {
        oop = oop.split("\n");
        //console.log("SPLIT", oop);
        let mark_pos = 26;
        let chars_parsed = 0;

        for (var idx in oop)
        {
            //console.log("CHARS PARSED", chars_parsed);
            let og = oop[idx];
            // Symbols: @, #, /, ?, :, ', !, $
            if (idx == 0 && oop[idx][0] && oop[idx][0] == "@")
                oop[idx] = `<span class='name'>@</span><span class='yellow'>${oop[idx].slice(1)}</span>`;
            else if (oop[idx][0] && oop[idx][0] == "#")
            {
                // Special case for #char
                if (oop[idx].indexOf("#char") == 0)
                {
                    oop[idx] = `<span class='command ch'>#</span>${oop[idx].slice(1, 6)}<span class="char" title="${int_to_char(oop[idx].slice(6))}">${oop[idx].slice(6)}</span>`;
                }
                else
                    oop[idx] = `<span class='command'>#</span>${oop[idx].slice(1)}`;
            }
            else if (oop[idx][0] && oop[idx][0] == "/")
            {
                oop[idx] = oop[idx].replace(/\//g, `<span class='go'>/</span>`);
            }
            else if (oop[idx][0] && oop[idx][0] == "?")
            {
                oop[idx] = oop[idx].replace(/\?/g, `<span class='try'>?</span>`);
            }
            else if (oop[idx][0] && oop[idx][0] == ":")
            {
                oop[idx] = `<span class='label'>:</span><span class='orange'>${oop[idx].slice(1)}</span>`;
            }
            else if (oop[idx][0] && oop[idx][0] == "'")
            {
                oop[idx] = `<span class='comment'>'${oop[idx].slice(1)}</span>`;
            }
            else if (oop[idx][0] && oop[idx][0] == "!" && (oop[idx].indexOf(";") != -1))
            {
                oop[idx] = `<span class='hyperlink'>!</span>\
<span class='label'>${oop[idx].slice(1, oop[idx].indexOf(";"))}</span>\
<span class='hyperlink'>;</span>\
${oop[idx].slice(oop[idx].indexOf(";")+1)}`;
            }
            else if (oop[idx][0] && oop[idx][0] == "$")
            {
                oop[idx] = `<span class='center'>$</span><span class=''>${oop[idx].slice(1)}</span>`;
            }
            chars_parsed += og.length + 1;
            if (mark_pos && (chars_parsed >= mark_pos))
            {
                //console.log(`[${chars_parsed}][${mark_pos}] Is this your line?`, oop[idx]);
                mark_pos = -1;
            }
        }
        return oop.join("\n");
    }

    get_bound_stat(stat)
    {
        if (stat.oop_length >= 0)
            return "<i>None</i>"
        return Math.abs(stat.oop_length);
    }

    get_color(color_id)
    {
        if (color_id == undefined)
            return `<i>None</i>`;
        let fg = color_id % 16
        let bg = parseInt(color_id / 16) % 8
        let bg_x = parseInt(fg * -8);
        let bg_y = parseInt(bg * -14);
        return `<div class='color-swatch' style='background-position: ${bg_x}px ${bg_y}px;position:relative;top:1px;'></div> ${this.color_names[fg]} on ${this.color_names[bg]}`;
    }

    get_step(stat)
    {
        const directions = {
            "0,0":"Idle",
            "1,0":"East",
            "1,1":"Southeast",
            "0,1":"South",
            "-1,1":"Southwest",
            "-1,0":"West",
            "-1,-1":"Northwest",
            "0,-1":"North",
            "1,-1":"Northeast",
        };

        let vector = [stat.step_x, stat.step_y].toString();
        let direction = directions[vector];
        if (direction == undefined)
            direction = "";
        else
            direction = " " + direction;
        let output = `(${stat.step_x}, ${stat.step_y})${direction}`
        return output
    }

    update_stat_sorting(e)
    {
        //console.log(e);
        let value = $("select[name=stat-sort]").val();
        let codeless = $("input[name=show-codeless]").prop("checked") ? true : false;
        this.config.stats.sort = value;
        this.config.stats.show_codeless = codeless;
        this.write_targets([{"target": "#stat-info", "html": this.write_stat_list()}]);
    }

    sort_stat_list_by_name()
    {
        if (! this.boards || ! this.selected_board)
            return [];
        let sorted = this.boards[this.selected_board].stats.slice();
        let board = this.boards[this.selected_board];

        sorted.sort(function(a, b){
            // TODO: Using stat_list_label and slicing makes this function easily break if formatting changes occur to stat list labels
            let raw_stat_name1 = ZZT_Handler.stat_list_label(a, board);
            let raw_stat_name2 = ZZT_Handler.stat_list_label(b, board);
            let stat_name_1 = raw_stat_name1.slice(raw_stat_name1.indexOf(")") + 1).toLowerCase()
            let stat_name_2 = raw_stat_name2.slice(raw_stat_name2.indexOf(")") + 1).toLowerCase()

            if (stat_name_1 < stat_name_2)
                    return -1;
                else if (stat_name_1 > stat_name_2)
                    return 1;
                else
                    return 0;
        });

        return sorted;
    }

    sort_stat_list_by_code()
    {
        let sorted = this.boards[this.selected_board].stats.slice();

        sorted.sort(function(a, b){
            if (a.oop_length < b.oop_length)
                return 1;
            else if (a.oop_length > b.oop_length)
                return -1;
            else
                return 0;
        });

        return sorted;
    }

    sort_stat_list_by_coords()
    {
        let sorted = this.boards[this.selected_board].stats.slice();
        console.log(sorted);

        sorted.sort(function(a, b){
            return (a.y * 60 + a.x) - (b.y * 60 + b.x);  // TODO Magic Number
        });

        return sorted;
    }

    sort_stat_list_by_index()
    {
        let sorted = this.boards[this.selected_board].stats.slice();
        return sorted;
    }

    code_search(query)
    {
        this.query = query;
        query = query.toLowerCase();
        let matches = {};
        let hashes = [];
        let match_count = 0;

        for (let board_idx in this.boards)
        {
            for (let stat_idx in this.boards[board_idx].stats)
            {
                let stat = this.boards[board_idx].stats[stat_idx];
                if (this.boards[board_idx].stats[stat_idx].oop.toLowerCase().indexOf(query) != -1)
                {
                    let hash = `${board_idx}-${stat_idx}`;
                    if (hashes.indexOf(hash) == -1)
                    {
                        hashes.push(hash);
                        if (matches["" + board_idx])
                            matches["" + board_idx].push(stat_idx);
                        else
                            matches["" + board_idx] = [stat_idx];
                        match_count++;
                    }
                }
            }
        }

        $(".code-search-no-results-message").html("&nbsp;");
        if (hashes.length)
        {
            $(".code-search-no-results-message").html(`<i>${match_count} match${(match_count > 1) ? 'es' : ''} found.</i>`);
            this.write_code_search_results_list(matches);
        }
        else
        {
            $(".code-search-no-results-message").html(`<i>No matching code found.</i>`);
            this.write_board_list();
        }
    }

    write_code_search_results_list(matches)
    {
        this.showing_search_results = true;
        console.log(matches);
        let output = `${this.filename}<ol class='board-list' start='0' data-fv_func='board_change'>\n`;
        let func = (this.config.pstrings.show_leftover_data) ? "revealed_string" : "toString";
        for (var idx = 0; idx < this.boards.length; idx++)
        {
            let chk_selected = (idx == this.selected_board) ? " selected" : "";
            let visible = (matches["" + idx]) ? "": " none";
            output += `<li class='board${chk_selected}${visible}' data-board-number=${idx} value="${idx}">` + this.boards[idx].title[func]() + "</li>\n";
            if (visible == "") // Matched board
            {
                for (let match_idx = 0; match_idx < matches["" + idx].length; match_idx++)
                {
                    // TODO: So much of this is copy/pasted
                    let stat = this.boards[idx].stats[matches["" + idx][match_idx]];
                    let name;

                    try {
                        let element = this.boards[idx].elements[stat.x][stat.y];
                        name = this.call_element_lookup(element.id).name;
                    }
                    catch (error)
                    {
                        name = "<i>Out of Bounds Stat</i>";
                    }
                    if (stat.oop[0] == "@")
                    {
                        name = stat.oop.slice(0, stat.oop.indexOf("\n"));
                    }
                    output += `<li class="stat-match" data-board-number=${idx} data-x="${stat.x}" data-y="${stat.y}">(${padded(stat.x)},${padded(stat.y)}) ${name} ${stat.oop_length} bytes</li>\n`;
                }
            }
        }
        output += "</ol>\n";

        this.write_targets([{"target": `.fv-content[data-fvpk="${this.fvpk}"]`, "html": output}])
    }

    get_preferences()
    {
        let output = "<h3>General</h3>";
        let config_key = this.get_config_key_for_handler();

        for (let idx=0; idx < this.config_fields.length; idx++)
        {
            output += this.get_config_field(this.config_fields[idx]);
        }

        output += this.renderer.get_preferences();

        return output;
    }

    coords_span(x, y)
    {
        return `<span class="coords" data-x="${x}" data-y="${y}">(${padded(x)}, ${padded(y)})</span>`;
    }

    get_zeta_live()
    {
        if (zfile_info && zfile_info.size > 10485760) // 10MB TODO
            return "<p><i>Play This Board</i> functionality is not available for this zipfile.</p>";
        return `<div style='margin-top:4px'><input type="button" id="play-board" value="Play This Board"> (Experimental. May not work as expected.)</div>`;
    }

    get_renderer_object_from_config()
    {
        console.log("Switching to renderer:", this.config.rendering_method.name)
        let temp_config = this.renderer.config;
        let renderer = null;

        // Create the new renderer
        switch (this.config.rendering_method.name) {
            case "ZZT Standard Renderer":
                renderer = new ZZT_Standard_Renderer(this.fvpk);
                break;
            case "ZZT Object Highlight Renderer":
                renderer = new ZZT_Object_Highlight_Renderer(this.fvpk);
                break;
            case "ZZT Code Highlight Renderer":
                renderer = new ZZT_Code_Highlight_Renderer(this.fvpk);
                break;
            case "ZZT Fake Wall Highlight Renderer":
                renderer = new ZZT_Fake_Wall_Highlight_Renderer(this.fvpk);
                break;
            default:
                console.log("Switching to DEFAULT renderer");
                renderer = new this.default_renderer(this.fvpk);
        };

        // Copy the current renderer's config to the new one
        renderer.config = temp_config;
        return renderer;
    }

    tool_disambiguate_board_titles(args)
    {
        console.log("I'M HERE");
        console.log(this);
        console.log(ALT_BOARD_TITLES);
        for (let idx in this.boards)
        {
            if (idx == 0)
                this.boards[idx].title.set_value(`Title Screen`);
            else if (idx < ALT_BOARD_TITLES.length)
                this.boards[idx].title.set_value(`${ALT_BOARD_TITLES[idx]}`);
            else
                this.boards[idx].title.set_value(`${ALT_BOARD_PREFIXES[parseInt(idx / 26)]} ${ALT_BOARD_TITLES[idx % 26]}`);
        }

        let target = {"target": `.fv-content[data-fvpk="${this.fvpk}"]`, "html": this.write_board_list()};
        this.write_targets([target]);
    }
}

export class SZZT_Handler extends ZZT_Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Super ZZT Handler";
        this.envelope_css_class = "szzt";
        this.default_renderer = SZZT_Standard_Renderer;
        this.renderer = new this.default_renderer(this.fvpk);

        this.first_board_start_idx = 1024;
        this.board_name_length = 60;
        this.max_flags = 16;
        this.max_stats = 128;
        this.board_width = 96;
        this.board_height = 80;
        this.tile_count = 7680;
    }

    static initial_config = {
        "pstrings": {
            "show_leftover_data": 0,
        },
        "stats": {
            "sort": "name",
            "show_codeless": 1,
        },
        "corrupt": {
            "enforce_stat_limit": 1,
        },
        "display": {
            "zoom": 1,
        },
        "oop": {
            "style": "modern",
        },
        "rendering_method": {
            "name": "SZZT_Standard_Renderer",
        },
    }

    static stat_list_label(stat, board)
    {
        let element, name;
        try {
            element = board.elements[stat.x][stat.y];
            name = SZZT_Handler.element_lookup(element.id).name;
        }
        catch (error)
        {
            console.log("ERROR IS", error);
            name = "<i>Out of Bounds Stat</i>";
        }
        if (stat.oop[0] == "@")
        {
            name = escape_html(stat.oop.slice(0, stat.oop.indexOf("\n")));
        }
        let byte_count = (stat.oop != "") ? ` ${stat.oop_length} bytes` : '';
        let output = `<a class="stat-link jsLink" data-x="${stat.x}" data-y="${stat.y}">(${padded(stat.x)}, ${padded(stat.y)}) ${name}</a>${byte_count}`;
        return output;
    }

    static element_lookup(idx) { return SZZT_ELEMENTS[idx]; }
    call_element_lookup(idx) { return SZZT_Handler.element_lookup(idx); }

    parse_world()
    {
        console.log("Parsing world for SZZT");
        let world = {};
        world.identifier = this.read_Int16();
        world.total_boards = this.read_Int16();
        world.ammo = this.read_Int16();
        world.gems = this.read_Int16();
        world.keys = this.read_keys();
        world.health = this.read_Int16();
        world.current_board = this.read_Int16();
        world.unused_szzt_1 = this.read_Int16();
        world.score = this.read_Int16();
        world.unused_szzt_2 = this.read_Int16();
        world.energizer_ticks = this.read_Int16();
        world.world_name = this.read_PString(20);
        world.flags = this.read_flags();
        world.board_time_seconds = this.read_Int16();
        world.board_time_hseconds = this.read_Int16(); // Hundredth-seconds
        world.is_save = this.read_Uint8();
        world.z = this.read_Int16();
        world.unused_szzt_3 = this.read_unused(11);
        return world;
    }

    get_world_info()
    {
        let output = `<div class="flex-table">`;
        let rows = [
            {"value": this.get_world_identifier(this.world.identifier), "label": "Format", },
            {"value": this.world.world_name, "label": "Name"},
            {"value": this.board_link(this.world.current_board), "label": "Starting Board", },
            {"value": this.world.total_boards, "label": "Total Boards", },
            {"value": this.world.health, "label": "Health", },
            {"value": this.world.ammo, "label": "Ammo", },
            {"value": this.world.gems, "label": "Gems", },
            {"value": this.get_keys_value(), "label": "Keys", },
            {"value": this.world.score, "label": "Score", },
            {"value": this.world.z, "label": this.get_z_counter_name(), },
            {"value": this.world.energizer_ticks, "label": "Energizer Ticks", },
            {"value": `${this.world.board_time_seconds}.${this.world.board_time_hseconds}`, "label": "Board Time", },
            {"value": this.yesno(this.world.is_save), "label": "Is Save", },
            //{"value": this.world.unused, "label": "", },
            {"value": this.get_flags_value(), "label": "Flags", },
            {"value": this.get_locks_value(), "label": "Detected Locks", },
        ];

        if (this.world.watermark)
        {
            rows.push({"value": this.world.watermark, "label": "Watermark"});
        }

        for (let i=0; i<rows.length; i++)
        {
            output += `<div class="flex-row"><div class="label">${rows[i].label}</div><div class="value">${rows[i].value}</div></div>\n`;
        }
        output += `</div>`;

        return output;
    }

    get_z_counter_name()
    {
        let counter_name = "Z";
        if (this.world.flags.length)
        {
            for (let idx in this.world.flags)
            {
                if (this.world.flags[idx].toString().toUpperCase()[0] == "Z")
                    counter_name = this.world.flags[idx].toString().toUpperCase().slice(1);
            }
        }
        return counter_name;
    }

    read_board_properties(board)
    {
        board.max_shots = this.read_Uint8();
        board.neighbor_boards = [this.read_Uint8(), this.read_Uint8(), this.read_Uint8(), this.read_Uint8()];
        board.reenter_when_zapped = this.read_Uint8();
        board.start_player_x = this.read_Uint8();
        board.start_player_y = this.read_Uint8();
        board.camera_x = this.read_Int16();
        board.camera_y = this.read_Int16();
        board.time_limit = this.read_Int16();
        board.unused = this.read_unused(14);
        board.stat_count = this.read_Int16();
        board.meta.stats_address += 30;
        return board;
    }

    get_board_info_rows(board)
    {
        let rows = [
            {"value": board.title.toString(), "label": "Title"}, // TODO: Should this respect show hidden data?
            {"value": `${board.max_shots} shots.`, "label": "Can Fire"},
            {"value": this.yesno(board.reenter_when_zapped), "label": "Re-enter When Zapped"},
            {"value": `${this.coords_span(board.start_player_x, board.start_player_y)}`, "label": "Re-enter X/Y"},
            {"value": `${this.coords_span(board.camera_x, board.camera_y)}`, "label": "Camera X/Y"},
            {"value": this.val_or_none(board.time_limit), "label": "Time Limit"},
            {"value": `${board.stat_count + 1} / ${this.max_stats + 1}`, "label": "Stat Count"},
            {"value": `${board.size} bytes`, "label": "Board Size"},
        ];
        return rows;
    }
}
