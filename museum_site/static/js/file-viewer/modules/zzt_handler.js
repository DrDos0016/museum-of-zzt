import { Handler } from "./handler.js";

export class ZZT_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "ZZT Handler";
        this.envelope_css_class = "zzt";
        this.world = {};
        this.boards = [];

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

    generate_html() {
        console.log("ZZT HTML Generation");
        let output = `<div style="flex:0 0 90%"><textarea style="width:90%;height:300px;">${JSON.stringify({"world": this.world, "boards": this.boards}, null, "\t")}</textarea>`;

        let temp = "";
        for (var idx = 0; idx < this.boards.length; idx++)
        {
            temp += this.boards[idx].title.debug() + "\n";
        }

        output += `<hr>${temp}</div>`
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
            let read_tiles = 0;
            while (read_tiles < this.tile_count)
            {
                let quantity = this.read_Uint8();
                let element = this.read_Uint8();
                let color = this.read_Uint8();
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
