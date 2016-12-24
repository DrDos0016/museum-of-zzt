// Oh man can this be optimized

class Renderer {
    constructor()
    {
        this.invisible_chars = {"revealed":178, "editor":176, "invisible":32};
        this.render = this.zzt_standard;
        this.invisible_style = $("select[name=invisibles]").val();
        this.bg_intensity = $("select[name=intensity]").val();
    }
    
    zzt_standard(board)
    {
        console.log("STANDARD RENDERING");
        console.log("Invis style:", this.invisible_style);
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
                    if (chunk[1] != 53)
                        print(ctx, chunk[2], ((chunk[1]-46)*16 + 15), x, y);
                    else // White Text needs black not gray background
                        print(ctx, chunk[2], 15, x, y);
                }
                else if (chunk[1] == 0) // Empty
                {
                    print(ctx, characters[chunk[1]], 0, x, y);
                }
                else if (board_number == 0 && chunk[1] == 4) // Replace Player w/ black on black (monitor) for title screen
                {
                    print(ctx, characters[chunk[1]], 0, x, y);
                }
                else if (chunk[1] == 36 || chunk[1] == 40 || chunk[1] == 30) // Objects, pushers, transporters, linewalls which need stat check (linewall 31)
                {
                    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
                    {
                        if (board.stats[stat_idx].x - 1 == x && board.stats[stat_idx].y - 1 == y)
                        {
                            if (chunk[1] == 36) // Object
                            {
                                print(ctx, board.stats[stat_idx].param1, chunk[2], x, y);
                            }
                            if (chunk[1] == 40) // Pusher
                            {
                                var pusher_char = 16;
                                if (board.stats[stat_idx].y_step > 32767)
                                    pusher_char = 30;
                                else if (board.stats[stat_idx].y_step > 0)
                                    pusher_char = 31;
                                else if (board.stats[stat_idx].x_step > 32767)
                                    pusher_char = 17;

                                print(ctx, pusher_char, chunk[2], x, y);
                            }
                            if (chunk[1] == 30) // Transporter
                            {
                                var transporter_char = 62;
                                if (board.stats[stat_idx].y_step > 32767)
                                    transporter_char = 94;
                                else if (board.stats[stat_idx].y_step > 0)
                                    transporter_char = 118;
                                else if (board.stats[stat_idx].x_step > 32767)
                                    transporter_char = 60;

                                print(ctx, transporter_char, chunk[2], x, y);
                            }
                        }
                    }
                }
                else if (chunk[1] == 31) // Line walls
                {
                    line_walls[(y*60)+x] = 1;
                    line_colors[(y*60)+x] = chunk[2];
                }
                else if (chunk[1] == 28) // Invisible walls
                {
                    print(ctx, this.invisible_chars[this.invisible_style], chunk[2], x, y);
                }
                else // Standard
                    print(ctx, characters[chunk[1]], chunk[2], x, y);

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
                    print(ctx, characters[chunk[1]], 0, x, y);
                }
                else if (board_number == 0 && chunk[1] == 4) // Replace Player w/ black on black (monitor) for title screen
                {
                    print(ctx, characters[chunk[1]], 0, x, y);
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
                                if (board.stats[stat_idx].y_step > 32767)
                                    pusher_char = 30;
                                else if (board.stats[stat_idx].y_step > 0)
                                    pusher_char = 31;
                                else if (board.stats[stat_idx].x_step > 32767)
                                    pusher_char = 17;

                                print(ctx, pusher_char, 8, x, y);
                            }
                            if (chunk[1] == 30) // Transporter
                            {
                                var transporter_char = 62;
                                if (board.stats[stat_idx].y_step > 32767)
                                    transporter_char = 94;
                                else if (board.stats[stat_idx].y_step > 0)
                                    transporter_char = 118;
                                else if (board.stats[stat_idx].x_step > 32767)
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
                    print(ctx, characters[chunk[1]], 8, x, y);

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
                    print(ctx, characters[chunk[1]], chunk[2], x, y);
                    
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
