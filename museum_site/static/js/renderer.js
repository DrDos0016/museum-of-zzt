// Oh man can this be optimized

class Renderer {
    constructor()
    {
        this.invisible_chars = {"revealed":178, "editor":176, "invisible":32};
        this.monitor_chars = {"hidden":32, "m":77};
        this.edge_chars = {"hidden":32, "e":69}; // Nice
        this.statlessobj_chars = {"hidden":32, "s":2};
        this.render = this.zzt_standard;
        this.invisible_style = $("select[name=invisibles]").val();
        this.monitor_style = $("select[name=monitors]").val();
        this.edge_style = $("select[name=edges]").val();
        this.statlessobj_style = $("select[name=statlessobj]").val();
        this.bg_intensity = $("select[name=intensity]").val();
    }

    zzt_standard(board)
    {
        /*console.log("STANDARD RENDERING");
        console.log("Invis style:", this.invisible_style);
        console.log("Monitor style:", this.monitor_style);
        console.log("Edge style:", this.edge_style);*/
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};

        for (var element_idx = 0; element_idx < board.elements.length; element_idx++)
        {
            var element = board.elements[element_idx];

            // Text
            if (element.id >= 47 && element.id <= 69)
            {
                if (element.id != 53)
                    print(ctx, element.color_id, ((element.id-46)*16 + 15), x, y);
                else // White Text needs black not gray background
                    print(ctx, element.color_id, 15, x, y);
            }
            else if (element.id == 0) // Empty
            {
                print(ctx, ENGINE.characters[element.id], 0, x, y);
            }
            else if (element.id == 36 || element.id == 40 || element.id == 30 || element.id == 13 || element.id == 12 ) // Pushers, transporters, bombs, dupes
            {
                print(ctx, ENGINE.characters[element.id], element.color_id, x, y); // Statless

                if (element.id == 36) // Objects
                {
                    print(ctx, this.statlessobj_chars[this.statlessobj_style], element.color_id, x, y);
                }


                for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                {

                    if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                    {
                        if (element.id == 36) // Object
                        {
                            print(ctx, board.stats[stat_idx].param1, element.color_id, x, y);
                        }
                        else if (element.id == 40) // Pusher
                        {
                            var pusher_char = 16;
                            if (board.stats[stat_idx].y_step < 0)
                                pusher_char = 30;
                            else if (board.stats[stat_idx].y_step > 0)
                                pusher_char = 31;
                            else if (board.stats[stat_idx].x_step < 0)
                                pusher_char = 17;

                            print(ctx, pusher_char, element.color_id, x, y);
                        }
                        else if (element.id == 30) // Transporter
                        {
                            var transporter_char = 62;
                            if (board.stats[stat_idx].y_step < 0)
                                transporter_char = 94;
                            else if (board.stats[stat_idx].y_step > 0)
                                transporter_char = 118;
                            else if (board.stats[stat_idx].x_step < 0)
                                transporter_char = 60;

                            print(ctx, transporter_char, element.color_id, x, y);
                        }
                        else if (element.id == 13) // Bomb
                        {
                            if (board.stats[stat_idx].param1 >= 2)
                            {
                                var bomb_char = board.stats[stat_idx].param1 + 48
                                if (bomb_char > 255)
                                    bomb_char -= 256;
                            }
                            else
                            {
                                continue; // Default is fine
                            }
                            print(ctx, bomb_char, element.color_id, x, y);
                        }
                        if (element.id == 12) // Duplicator
                        {
                            var dupe_chars = [250,250,249,248,111,79];
                            if (board.stats[stat_idx].param1 >= 2 && board.stats[stat_idx].param1 <= 5)
                                print(ctx, dupe_chars[board.stats[stat_idx].param1], element.color_id, x, y);
                            // Default case handles the rest



                        }
                    }
                }
            }
            else if (element.id == 31) // Line walls
            {
                line_walls[(y*60)+x] = 1;
                line_colors[(y*60)+x] = element.color_id;
            }
            else if (element.id == 28) // Invisible walls
            {
                print(ctx, this.invisible_chars[this.invisible_style], element.color_id, x, y);
            }
            else if (element.id == 3) // Monitors
            {
                print(ctx, this.monitor_chars[this.monitor_style], element.color_id, x, y);
            }
            else if (element.id == 1) // Board Edges
            {
                print(ctx, this.edge_chars[this.edge_style], element.color_id, x, y);
                line_walls[(y*60)+x] = 2; // Board edges count as line wall connections
            }
            else // Standard
                print(ctx, ENGINE.characters[element.id], element.color_id, x, y);

            tile += 1;
            x += 1;
            if (x > 59)
            {
                x = 0;
                y += 1;
            }
        }


        // Render line walls
        var line_tiles = Object.keys(line_walls);
        for (var line_idx = 0; line_idx < 1500; line_idx++)
        {
            var line_key = "";
            if (line_idx < 60)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-60] ? "1" : "0");

            if (line_idx >= 1440)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+60] ? "1" : "0");

            if (line_idx % 60 == 59)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+1] ? "1" : "0");

            if (line_idx % 60 == 0)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-1] ? "1" : "0");

            if (line_walls[line_idx] && line_walls[line_idx] != 2)
            {
                print(ctx, line_characters[line_key], line_colors[line_idx], line_idx % 60, parseInt(line_idx / 60));
            }
        }
    }

    weave_standard(board)
    {
        /*console.log("STANDARD RENDERING");
        console.log("Invis style:", this.invisible_style);
        console.log("Monitor style:", this.monitor_style);
        console.log("Edge style:", this.edge_style);*/
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};

        for (var element_idx = 0; element_idx < board.elements.length; element_idx++)
        {
            var element = board.elements[element_idx];

            // Text
            if (element.id >= 47 && element.id <= 69)
            {
                if (element.id != 53)
                    print(ctx, element.color_id, ((element.id-46)*16 + 15), x, y);
                else // White Text needs black not gray background
                    print(ctx, element.color_id, 15, x, y);
            }
            else if (element.id >= 128) // Weave Custom Text
            {
                print(ctx, element.color_id, (element.id - 128), x, y);
            }
            else if (element.id == 0) // Empty
            {
                print(ctx, ENGINE.characters[element.id], 0, x, y);
            }
            else if (element.id == 36 || element.id == 40 || element.id == 30 || element.id == 13 || element.id == 12 ) // Pushers, transporters, bombs, dupes
            {
                print(ctx, ENGINE.characters[element.id], element.color_id, x, y); // Statless

                if (element.id == 36) // Objects
                {
                    print(ctx, this.statlessobj_chars[this.statlessobj_style], element.color_id, x, y);
                }


                for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                {

                    if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                    {
                        if (element.id == 36) // Object
                        {
                            print(ctx, board.stats[stat_idx].param1, element.color_id, x, y);
                        }
                        else if (element.id == 40) // Pusher
                        {
                            var pusher_char = 16;
                            if (board.stats[stat_idx].y_step < 0)
                                pusher_char = 30;
                            else if (board.stats[stat_idx].y_step > 0)
                                pusher_char = 31;
                            else if (board.stats[stat_idx].x_step < 0)
                                pusher_char = 17;

                            print(ctx, pusher_char, element.color_id, x, y);
                        }
                        else if (element.id == 30) // Transporter
                        {
                            var transporter_char = 62;
                            if (board.stats[stat_idx].y_step < 0)
                                transporter_char = 94;
                            else if (board.stats[stat_idx].y_step > 0)
                                transporter_char = 118;
                            else if (board.stats[stat_idx].x_step < 0)
                                transporter_char = 60;

                            print(ctx, transporter_char, element.color_id, x, y);
                        }
                        else if (element.id == 13) // Bomb
                        {
                            if (board.stats[stat_idx].param1 >= 2)
                            {
                                var bomb_char = board.stats[stat_idx].param1 + 48
                                if (bomb_char > 255)
                                    bomb_char -= 256;
                            }
                            else
                            {
                                continue; // Default is fine
                            }
                            print(ctx, bomb_char, element.color_id, x, y);
                        }
                        if (element.id == 12) // Duplicator
                        {
                            var dupe_chars = [250,250,249,248,111,79];
                            if (board.stats[stat_idx].param1 >= 2 && board.stats[stat_idx].param1 <= 5)
                                print(ctx, dupe_chars[board.stats[stat_idx].param1], element.color_id, x, y);
                            // Default case handles the rest



                        }
                    }
                }
            }
            else if (element.id == 31) // Line walls
            {
                line_walls[(y*60)+x] = 1;
                line_colors[(y*60)+x] = element.color_id;
            }
            else if (element.id == 28) // Invisible walls
            {
                print(ctx, this.invisible_chars[this.invisible_style], element.color_id, x, y);
            }
            else if (element.id == 3) // Monitors
            {
                print(ctx, this.monitor_chars[this.monitor_style], element.color_id, x, y);
            }
            else if (element.id == 1) // Board Edges
            {
                print(ctx, this.edge_chars[this.edge_style], element.color_id, x, y);
                line_walls[(y*60)+x] = 2; // Board edges count as line wall connections
            }
            else // Standard
                print(ctx, ENGINE.characters[element.id], element.color_id, x, y);

            tile += 1;
            x += 1;
            if (x > 59)
            {
                x = 0;
                y += 1;
            }
        }


        // Render line walls
        var line_tiles = Object.keys(line_walls);
        for (var line_idx = 0; line_idx < 1500; line_idx++)
        {
            var line_key = "";
            if (line_idx < 60)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-60] ? "1" : "0");

            if (line_idx >= 1440)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+60] ? "1" : "0");

            if (line_idx % 60 == 59)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+1] ? "1" : "0");

            if (line_idx % 60 == 0)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-1] ? "1" : "0");

            if (line_walls[line_idx] && line_walls[line_idx] != 2)
            {
                print(ctx, line_characters[line_key], line_colors[line_idx], line_idx % 60, parseInt(line_idx / 60));
            }
        }
    }

    zzt_objects(board)
    {
        console.log("OBJECT RENDERING");
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};

        for (var chunk_idx = 0; chunk_idx < board.room.length; chunk_idx++)
        {
            var chunk = board.room[chunk_idx];

            for (var qty = 0; qty < chunk[0]; qty++)
            {
                // Text
                if (chunk[1] >= 47 && chunk[1] <= 69)
                {
                    print(ctx, chunk[2], 8, x, y);
                }
                else if (chunk[1] == 0) // Empty
                {
                    print(ctx, ENGINE.characters[chunk[1]], 0, x, y);
                }
                else if (board_number == 0 && chunk[1] == 4) // Replace Player w/ black on black (monitor) for title screen
                {
                    print(ctx, ENGINE.characters[chunk[1]], 0, x, y);
                }
                else if (chunk[1] == 36 || chunk[1] == 40 || chunk[1] == 30) // Objects, pushers, transporters, linewalls which need stat check (linewall 31)
                {
                    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                    {
                        if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                        {
                            if (chunk[1] == 36) // Object
                            {
                                print(ctx, 33, 14, x, y);
                            }
                            if (chunk[1] == 40) // Pusher
                            {
                                var pusher_char = 16;
                                if (board.stats[stat_idx].y_step < 0)
                                    pusher_char = 30;
                                else if (board.stats[stat_idx].y_step > 0)
                                    pusher_char = 31;
                                else if (board.stats[stat_idx].x_step < 0)
                                    pusher_char = 17;

                                print(ctx, pusher_char, 8, x, y);
                            }
                            if (chunk[1] == 30) // Transporter
                            {
                                var transporter_char = 62;
                                if (board.stats[stat_idx].y_step < 0)
                                    transporter_char = 94;
                                else if (board.stats[stat_idx].y_step > 0)
                                    transporter_char = 118;
                                else if (board.stats[stat_idx].x_step < 0)
                                    transporter_char = 60;

                                print(ctx, transporter_char, 8, x, y);
                            }
                        }
                    }
                }
                else if (chunk[1] == 31) // Line walls
                {
                    line_walls[(y*60)+x] = 1;
                    line_colors[(y*60)+x] = 8;
                }
                else // Standard
                    print(ctx, ENGINE.characters[chunk[1]], 8, x, y);

                tile += 1;
                x += 1;
                if (x > 59)
                {
                    x = 0;
                    y += 1;
                }
            }
        }

        // Render line walls
        var line_tiles = Object.keys(line_walls);
        for (var line_idx = 0; line_idx < 1500; line_idx++)
        {
            var line_key = "";
            if (line_idx < 60)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-60] ? "1" : "0");

            if (line_idx > 1440)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+60] ? "1" : "0");

            if (line_idx % 60 == 59)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+1] ? "1" : "0");

            if (line_idx % 60 == 0)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-1] ? "1" : "0");

            if (line_walls[line_idx])
            {
                print(ctx, line_characters[line_key], 8, line_idx % 60, parseInt(line_idx / 60));
            }
        }
    }

    zzt_code(board)
    {
        console.log("CODE RENDERING");
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};

        for (var chunk_idx = 0; chunk_idx < board.room.length; chunk_idx++)
        {
            var chunk = board.room[chunk_idx];

            for (var qty = 0; qty < chunk[0]; qty++)
            {
                // Text
                if (chunk[1] >= 47 && chunk[1] <= 69)
                {
                    print(ctx, chunk[2], 8, x, y);
                }
                else if (chunk[1] == 0) // Empty
                {
                    print(ctx, ENGINE.characters[chunk[1]], 0, x, y);
                }
                else if (board_number == 0 && chunk[1] == 4) // Replace Player w/ black on black (monitor) for title screen
                {
                    print(ctx, ENGINE.characters[chunk[1]], 0, x, y);
                }
                else if (chunk[1] == 36 || chunk[1] == 40 || chunk[1] == 30 || chunk[1] == 10) // Objects, pushers, transporters, linewalls, SCROLLS which need stat check (linewall 31)
                {
                    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                    {
                        if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                        {
                            if (chunk[1] == 10) // Scroll
                            {
                                if (board.stats[stat_idx].oop)
                                    print(ctx, 33, 14, x, y);
                                else
                                    print(ctx, ENGINE.characters[chunk[1]], 8, x, y);
                            }
                            if (chunk[1] == 36) // Object
                            {
                                if (board.stats[stat_idx].oop)
                                    print(ctx, 33, 14, x, y);
                                else
                                    print(ctx, board.stats[stat_idx].param1, 8, x, y);
                            }
                            if (chunk[1] == 40) // Pusher
                            {
                                var pusher_char = 16;
                                if (board.stats[stat_idx].y_step < 0)
                                    pusher_char = 30;
                                else if (board.stats[stat_idx].y_step > 0)
                                    pusher_char = 31;
                                else if (board.stats[stat_idx].x_step < 0)
                                    pusher_char = 17;

                                print(ctx, pusher_char, 8, x, y);
                            }
                            if (chunk[1] == 30) // Transporter
                            {
                                var transporter_char = 62;
                                if (board.stats[stat_idx].y_step < 0)
                                    transporter_char = 94;
                                else if (board.stats[stat_idx].y_step > 0)
                                    transporter_char = 118;
                                else if (board.stats[stat_idx].x_step < 0)
                                    transporter_char = 60;

                                print(ctx, transporter_char, 8, x, y);
                            }
                        }
                    }
                }
                else if (chunk[1] == 31) // Line walls
                {
                    line_walls[(y*60)+x] = 1;
                    line_colors[(y*60)+x] = 8;
                }
                else // Standard
                    print(ctx, ENGINE.characters[chunk[1]], 8, x, y);

                tile += 1;
                x += 1;
                if (x > 59)
                {
                    x = 0;
                    y += 1;
                }
            }
        }

        // Render line walls
        var line_tiles = Object.keys(line_walls);
        for (var line_idx = 0; line_idx < 1500; line_idx++)
        {
            var line_key = "";
            if (line_idx < 60)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-60] ? "1" : "0");

            if (line_idx > 1440)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+60] ? "1" : "0");

            if (line_idx % 60 == 59)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+1] ? "1" : "0");

            if (line_idx % 60 == 0)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-1] ? "1" : "0");

            if (line_walls[line_idx])
            {
                print(ctx, line_characters[line_key], 8, line_idx % 60, parseInt(line_idx / 60));
            }
        }
    }

    zzt_dark(board)
    {
        console.log("DARK RENDERING");
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};

        for (var chunk_idx = 0; chunk_idx < board.room.length; chunk_idx++)
        {
            var chunk = board.room[chunk_idx];

            for (var qty = 0; qty < chunk[0]; qty++)
            {
                if ([4, 6, 11].indexOf(chunk[1]) == -1) // Render darkness
                    print(ctx, 176, 7, x, y);
                else // Standard
                    print(ctx, ENGINE.characters[chunk[1]], chunk[2], x, y);

                tile += 1;
                x += 1;
                if (x > 59)
                {
                    x = 0;
                    y += 1;
                }
            }
        }
    }

    zzt_fake(board)
    {
        console.log("FAKE WALLS RENDERING");
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};

        for (var chunk_idx = 0; chunk_idx < board.room.length; chunk_idx++)
        {
            var chunk = board.room[chunk_idx];

            for (var qty = 0; qty < chunk[0]; qty++)
            {
                // Text
                if (chunk[1] >= 47 && chunk[1] <= 69)
                {
                    print(ctx, chunk[2], 8, x, y);
                }
                else if (chunk[1] == 0) // Empty
                {
                    print(ctx, ENGINE.characters[chunk[1]], 0, x, y);
                }
                else if (board_number == 0 && chunk[1] == 4) // Replace Player w/ black on black (monitor) for title screen
                {
                    print(ctx, ENGINE.characters[chunk[1]], 0, x, y);
                }
                else if (chunk[1] == 36 || chunk[1] == 40 || chunk[1] == 30) // Objects, pushers, transporters, linewalls which need stat check (linewall 31)
                {
                    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                    {
                        if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                        {
                            if (chunk[1] == 36) // Object
                            {
                                print(ctx, board.stats[stat_idx].param1, 8, x, y);
                            }
                            if (chunk[1] == 40) // Pusher
                            {
                                var pusher_char = 16;
                                if (board.stats[stat_idx].y_step < 0)
                                    pusher_char = 30;
                                else if (board.stats[stat_idx].y_step > 0)
                                    pusher_char = 31;
                                else if (board.stats[stat_idx].x_step < 0)
                                    pusher_char = 17;

                                print(ctx, pusher_char, 8, x, y);
                            }
                            if (chunk[1] == 30) // Transporter
                            {
                                var transporter_char = 62;
                                if (board.stats[stat_idx].y_step < 0)
                                    transporter_char = 94;
                                else if (board.stats[stat_idx].y_step > 0)
                                    transporter_char = 118;
                                else if (board.stats[stat_idx].x_step < 0)
                                    transporter_char = 60;

                                print(ctx, transporter_char, 8, x, y);
                            }
                        }
                    }
                }
                else if (chunk[1] == 31) // Line walls
                {
                    line_walls[(y*60)+x] = 1;
                    line_colors[(y*60)+x] = 8;
                }
                else if (chunk[1] == 27) // Fake walls
                    print(ctx, ENGINE.characters[chunk[1]], 14, x, y);
                else // Standard
                    print(ctx, ENGINE.characters[chunk[1]], 8, x, y);

                tile += 1;
                x += 1;
                if (x > 59)
                {
                    x = 0;
                    y += 1;
                }
            }
        }

        // Render line walls
        var line_tiles = Object.keys(line_walls);
        for (var line_idx = 0; line_idx < 1500; line_idx++)
        {
            var line_key = "";
            if (line_idx < 60)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-60] ? "1" : "0");

            if (line_idx > 1440)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+60] ? "1" : "0");

            if (line_idx % 60 == 59)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+1] ? "1" : "0");

            if (line_idx % 60 == 0)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-1] ? "1" : "0");

            if (line_walls[line_idx])
            {
                print(ctx, line_characters[line_key], 8, line_idx % 60, parseInt(line_idx / 60));
            }
        }
    }

    zzt_empty(board)
    {
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};

        for (var element_idx = 0; element_idx < board.elements.length; element_idx++)
        {
            var element = board.elements[element_idx];

            // Text
            if (element.id >= 47 && element.id <= 69)
            {
                if (element.id != 53)
                    print(ctx, element.color_id, ((element.id-46)*16 + 15), x, y);
                else // White Text needs black not gray background
                    print(ctx, element.color_id, 15, x, y);
            }
            else if (element.id == 0) // Empty
            {
                print(ctx, 7, element.color_id, x, y);
            }
            else if (element.id == 36 || element.id == 40 || element.id == 30 || element.id == 13 || element.id == 12 ) // Objects, pushers, transporters, bombs, dupes
            {
                print(ctx, ENGINE.characters[element.id], element.color_id, x, y); // Statless
                for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                {

                    if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                    {
                        if (element.id == 36) // Object
                        {
                            print(ctx, board.stats[stat_idx].param1, element.color_id, x, y);
                        }
                        else if (element.id == 40) // Pusher
                        {
                            var pusher_char = 16;
                            if (board.stats[stat_idx].y_step < 0)
                                pusher_char = 30;
                            else if (board.stats[stat_idx].y_step > 0)
                                pusher_char = 31;
                            else if (board.stats[stat_idx].x_step < 0)
                                pusher_char = 17;

                            print(ctx, pusher_char, element.color_id, x, y);
                        }
                        else if (element.id == 30) // Transporter
                        {
                            var transporter_char = 62;
                            if (board.stats[stat_idx].y_step < 0)
                                transporter_char = 94;
                            else if (board.stats[stat_idx].y_step > 0)
                                transporter_char = 118;
                            else if (board.stats[stat_idx].x_step < 0)
                                transporter_char = 60;

                            print(ctx, transporter_char, element.color_id, x, y);
                        }
                        else if (element.id == 13) // Bomb
                        {
                            if (board.stats[stat_idx].param1 >= 2)
                            {
                                var bomb_char = board.stats[stat_idx].param1 + 48
                                if (bomb_char > 255)
                                    bomb_char -= 256;
                            }
                            else
                            {
                                continue; // Default is fine
                            }
                            print(ctx, bomb_char, element.color_id, x, y);
                        }
                        if (element.id == 12) // Duplicator
                        {
                            var dupe_chars = [250,250,249,248,111,79];
                            if (board.stats[stat_idx].param1 >= 2 && board.stats[stat_idx].param1 <= 5)
                                print(ctx, dupe_chars[board.stats[stat_idx].param1], element.color_id, x, y);
                            // Default case handles the rest



                        }
                    }
                }
            }
            else if (element.id == 31) // Line walls
            {
                line_walls[(y*60)+x] = 1;
                line_colors[(y*60)+x] = element.color_id;
            }
            else if (element.id == 28) // Invisible walls
            {
                print(ctx, this.invisible_chars[this.invisible_style], element.color_id, x, y);
            }
            else if (element.id == 3) // Monitors
            {
                print(ctx, this.monitor_chars[this.monitor_style], element.color_id, x, y);
            }
            else if (element.id == 1) // Board Edges
            {
                print(ctx, this.edge_chars[this.edge_style], element.color_id, x, y);
            }
            else // Standard
                print(ctx, ENGINE.characters[element.id], element.color_id, x, y);

            tile += 1;
            x += 1;
            if (x > 59)
            {
                x = 0;
                y += 1;
            }
        }


        // Render line walls
        var line_tiles = Object.keys(line_walls);
        for (var line_idx = 0; line_idx < 1500; line_idx++)
        {
            var line_key = "";
            if (line_idx < 60)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-60] ? "1" : "0");

            if (line_idx >= 1440)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+60] ? "1" : "0");

            if (line_idx % 60 == 59)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+1] ? "1" : "0");

            if (line_idx % 60 == 0)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-1] ? "1" : "0");

            if (line_walls[line_idx])
            {
                print(ctx, line_characters[line_key], line_colors[line_idx], line_idx % 60, parseInt(line_idx / 60));
            }
        }
    }

    zzt_empty_text(board)
    {
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};

        for (var element_idx = 0; element_idx < board.elements.length; element_idx++)
        {
            var element = board.elements[element_idx];

            // Text
            if (element.id >= 47 && element.id <= 69)
            {
                if (element.id != 53)
                    print(ctx, element.color_id, ((element.id-46)*16 + 15), x, y);
                else // White Text needs black not gray background
                    print(ctx, element.color_id, 15, x, y);
            }
            else if (element.id == 0) // Empty
            {
                print(ctx, element.color_id, 7, x, y); // Text finder
            }
            else if (element.id == 36 || element.id == 40 || element.id == 30 || element.id == 13 || element.id == 12 ) // Objects, pushers, transporters, bombs, dupes
            {
                print(ctx, ENGINE.characters[element.id], element.color_id, x, y); // Statless
                for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                {

                    if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                    {
                        if (element.id == 36) // Object
                        {
                            print(ctx, board.stats[stat_idx].param1, element.color_id, x, y);
                        }
                        else if (element.id == 40) // Pusher
                        {
                            var pusher_char = 16;
                            if (board.stats[stat_idx].y_step < 0)
                                pusher_char = 30;
                            else if (board.stats[stat_idx].y_step > 0)
                                pusher_char = 31;
                            else if (board.stats[stat_idx].x_step < 0)
                                pusher_char = 17;

                            print(ctx, pusher_char, element.color_id, x, y);
                        }
                        else if (element.id == 30) // Transporter
                        {
                            var transporter_char = 62;
                            if (board.stats[stat_idx].y_step < 0)
                                transporter_char = 94;
                            else if (board.stats[stat_idx].y_step > 0)
                                transporter_char = 118;
                            else if (board.stats[stat_idx].x_step < 0)
                                transporter_char = 60;

                            print(ctx, transporter_char, element.color_id, x, y);
                        }
                        else if (element.id == 13) // Bomb
                        {
                            if (board.stats[stat_idx].param1 >= 2)
                            {
                                var bomb_char = board.stats[stat_idx].param1 + 48
                                if (bomb_char > 255)
                                    bomb_char -= 256;
                            }
                            else
                            {
                                continue; // Default is fine
                            }
                            print(ctx, bomb_char, element.color_id, x, y);
                        }
                        if (element.id == 12) // Duplicator
                        {
                            var dupe_chars = [250,250,249,248,111,79];
                            if (board.stats[stat_idx].param1 >= 2 && board.stats[stat_idx].param1 <= 5)
                                print(ctx, dupe_chars[board.stats[stat_idx].param1], element.color_id, x, y);
                            // Default case handles the rest



                        }
                    }
                }
            }
            else if (element.id == 31) // Line walls
            {
                line_walls[(y*60)+x] = 1;
                line_colors[(y*60)+x] = element.color_id;
            }
            else if (element.id == 28) // Invisible walls
            {
                print(ctx, this.invisible_chars[this.invisible_style], element.color_id, x, y);
            }
            else if (element.id == 3) // Monitors
            {
                print(ctx, this.monitor_chars[this.monitor_style], element.color_id, x, y);
            }
            else if (element.id == 1) // Board Edges
            {
                print(ctx, this.edge_chars[this.edge_style], element.color_id, x, y);
            }
            else // Standard
                print(ctx, ENGINE.characters[element.id], element.color_id, x, y);

            tile += 1;
            x += 1;
            if (x > 59)
            {
                x = 0;
                y += 1;
            }
        }


        // Render line walls
        var line_tiles = Object.keys(line_walls);
        for (var line_idx = 0; line_idx < 1500; line_idx++)
        {
            var line_key = "";
            if (line_idx < 60)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-60] ? "1" : "0");

            if (line_idx >= 1440)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+60] ? "1" : "0");

            if (line_idx % 60 == 59)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+1] ? "1" : "0");

            if (line_idx % 60 == 0)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-1] ? "1" : "0");

            if (line_walls[line_idx])
            {
                print(ctx, line_characters[line_key], line_colors[line_idx], line_idx % 60, parseInt(line_idx / 60));
            }
        }
    }

    szzt_standard(board)
    {
        console.log("SUPER ZZT STANDARD RENDERING");
        console.log("Invis style:", this.invisible_style);
        console.log("Monitor style:", this.monitor_style);
        console.log("Edge style:", this.edge_style);
        var x = 0;
        var y = 0;
        var tile = 0;
        var line_walls = {}; // I am not happy with this solution
        var line_colors = {};
        var webs = {};
        var web_colors = {};

        for (var chunk_idx = 0; chunk_idx < board.room.length; chunk_idx++)
        {
            var chunk = board.room[chunk_idx];

            for (var qty = 0; qty < chunk[0]; qty++)
            {
                // Text
                if (chunk[1] >= 73 && chunk[1] <= 79)
                {
                    if (chunk[1] != 79)
                        print(ctx, chunk[2], ((chunk[1]-72)*16 + 15), x, y);
                    else // White Text needs black not gray background
                        print(ctx, chunk[2], 15, x, y);
                }
                else if (chunk[1] == 0) // Empty
                {
                    print(ctx, ENGINE.characters[chunk[1]], 0, x, y);
                }
                else if (chunk[1] == 36 || chunk[1] == 40 || chunk[1] == 30 || chunk[1] == 13 || chunk[1] == 12 ) // Objects, pushers, transporters, bombs, dupes
                {
                    print(ctx, ENGINE.characters[chunk[1]], chunk[2], x, y); // Statless
                    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                    {

                        if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                        {
                            if (chunk[1] == 36) // Object
                            {
                                print(ctx, board.stats[stat_idx].param1, chunk[2], x, y);
                            }
                            else if (chunk[1] == 40) // Pusher
                            {
                                var pusher_char = 16;
                                if (board.stats[stat_idx].y_step < 0)
                                    pusher_char = 30;
                                else if (board.stats[stat_idx].y_step > 0)
                                    pusher_char = 31;
                                else if (board.stats[stat_idx].x_step < 0)
                                    pusher_char = 17;

                                print(ctx, pusher_char, chunk[2], x, y);
                            }
                            else if (chunk[1] == 30) // Transporter
                            {
                                var transporter_char = 62;
                                if (board.stats[stat_idx].y_step < 0)
                                    transporter_char = 94;
                                else if (board.stats[stat_idx].y_step > 0)
                                    transporter_char = 118;
                                else if (board.stats[stat_idx].x_step < 0)
                                    transporter_char = 60;

                                print(ctx, transporter_char, chunk[2], x, y);
                            }
                            else if (chunk[1] == 13) // Bomb
                            {
                                if (board.stats[stat_idx].param1 >= 2)
                                {
                                    var bomb_char = board.stats[stat_idx].param1 + 48
                                    if (bomb_char > 255)
                                        bomb_char -= 256;
                                }
                                else
                                {
                                    continue; // Default is fine
                                }
                                print(ctx, bomb_char, chunk[2], x, y);
                            }
                            if (chunk[1] == 12) // Duplicator
                            {
                                var dupe_chars = [250,250,249,248,111,79];
                                if (board.stats[stat_idx].param1 >= 2 && board.stats[stat_idx].param1 <= 5)
                                    print(ctx, dupe_chars[board.stats[stat_idx].param1], chunk[2], x, y);
                                // Default case handles the rest
                            }
                        }
                    }
                }
                else if (chunk[1] == 31) // Line walls
                {
                    line_walls[(y*96)+x] = 1;
                    line_colors[(y*96)+x] = chunk[2];
                }
                else if (chunk[1] == 63) // Webs
                {
                    webs[(y*96)+x] = 1;
                    web_colors[(y*96)+x] = chunk[2];
                }
                else if (chunk[1] == 28) // Invisible walls
                {
                    print(ctx, this.invisible_chars[this.invisible_style], chunk[2], x, y);
                }
                else if (chunk[1] == 3) // Monitors
                {
                    print(ctx, this.monitor_chars[this.monitor_style], chunk[2], x, y);
                }
                else if (chunk[1] == 1) // Board Edges
                {
                    print(ctx, this.edge_chars[this.edge_style], chunk[2], x, y);
                }
                else // Standard
                    print(ctx, ENGINE.characters[chunk[1]], chunk[2], x, y);

                tile += 1;
                x += 1;
                if (x > 95)
                {
                    x = 0;
                    y += 1;
                }
            }
        }

        // Render line walls
        var line_tiles = Object.keys(line_walls);
        for (var line_idx = 0; line_idx < 7680; line_idx++)
        {
            var line_key = "";
            if (line_idx < 96)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-96] ? "1" : "0");

            if (line_idx >= 7584)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+96] ? "1" : "0");

            if (line_idx % 96 == 95)
                line_key += "1";
            else
                line_key += (line_walls[line_idx+1] ? "1" : "0");

            if (line_idx % 96 == 0)
                line_key += "1";
            else
                line_key += (line_walls[line_idx-1] ? "1" : "0");

            if (line_walls[line_idx])
            {
                print(ctx, line_characters[line_key], line_colors[line_idx], line_idx % 96, parseInt(line_idx / 96));
            }
        }


        // We also need a list of things on top of webs
        for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
        {
            if (board.stats[stat_idx].under_id == 63) // Web
            {
                var x_coord = board.stats[stat_idx].x;
                var y_coord = board.stats[stat_idx].y;
                var tile_idx = board.stats[stat_idx].tile_idx;
                var under_color = board.stats[stat_idx].under_color;

                webs[tile_idx] = 2; // I'll regret doing it like this later, but I'm making sure that things on webs are drawn instead of the webs meant to be beneath them with this
                web_colors[tile_idx] = under_color;
            }
        }

        // Render webs
        var web_tiles = Object.keys(webs);

        for (var web_idx = 0; web_idx < 7680; web_idx++)
        {
            var web_key = "";
            if (web_idx < 96)
                web_key += "1";
            else
                web_key += (webs[web_idx-96] ? "1" : "0");

            if (web_idx >= 7584)
                web_key += "1";
            else
                web_key += (webs[web_idx+96] ? "1" : "0");

            if (web_idx % 96 == 95)
                web_key += "1";
            else
                web_key += (webs[web_idx+1] ? "1" : "0");

            if (web_idx % 96 == 0)
                web_key += "1";
            else
                web_key += (webs[web_idx-1] ? "1" : "0");

            if (webs[web_idx] && webs[web_idx] != 2)
            {
                print(ctx, web_characters[web_key], web_colors[web_idx], web_idx % 96, parseInt(web_idx / 96));
            }
        }
    }
};

/* Canvas functions */
function print(ctx, character, color, x, y)
{
    var ch_x = character % 16;
    var ch_y = parseInt(character / 16);
    var fg = colors[color % 16];

    if (renderer.bg_intensity == "low")
        var bg = colors[parseInt(color / 16) % 8];
    else if (renderer.bg_intensity == "high")
        var bg = colors[parseInt(color / 16)];

    // Background
    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = bg;
    ctx.fillRect(x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT);

    // Creates transparency for foreground
    ctx.globalCompositeOperation = "xor";
    ctx.drawImage(CHARSET_IMAGE, ch_x*TILE_WIDTH, ch_y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT, x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT);
    // Draw foreground
    ctx.globalCompositeOperation = "destination-over";
    ctx.fillStyle = fg;
    ctx.fillRect(x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT);
    return true;
}
/* End Canvas functions */
