var elements = ["Empty", "Board Edge", "Messenger", "Monitor", "Player", "Ammo", "Torch", "Gem", "Key", "Door", "Scroll", "Passage", "Duplicator", "Bomb", "Energizer", "Star", "Conveyor, Clockwise", "Conveyor, Counterclockwise", "Bullet", "Water", "Forest", "Solid Wall", "Normal Wall", "Breakable Wall", "Boulder", "Slider, North-South", "Slider, East-West", "Fake Wall", "Invisible Wall", "Blink Wall", "Transporter", "Line Wall", "Ricochet", "Blink Ray, Horizontal", "Bear", "Ruffian", "Object", "Slime", "Shark", "Spinning Gun", "Pusher", "Lion", "Tiger", "Blink Ray, Vertical", "Centipede Head", "Centipede Segment", "Text, Blue", "Text, Green", "Text, Cyan", "Text, Red", "Text, Purple", "Text, Brown", "Text, Black"];
//var colors = ["black", "dblue", "dgreen", "dcyan", "dred", "dpurple", "dyellow", "gray", "dgray", "blue", "green", "cyan", "red", "purple", "yellow", "white"];
var colors = ["#000000", "#0000AA", "#00AA00", "#00AAAA", "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA", "#555555", "#5555FF", "#55FF55", "#55FFFF", "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF"];
var characters = [32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 47, 47, 248, 176, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 62, 249, 42, 205, 153, 5, 2, 42, 94, 24, 16, 234, 227, 186, 233, 79, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63];
var world = null;

var World = function (data) {
    // World Properties
    this.hex = data;                    // World file as hex string
    this.idx = 0;                       // Index of world file data
    this.flags = [];                    // List of flags
    this.boards = [];                   // List of boards
    
    // World Methods
    this.read = function (bytes)        // read X bytes of world file data
    {
        var input = this.hex.substr(this.idx, bytes*2);
        output = input;
        
        // Convert to Little Endian
        if (bytes > 1)
        {
            var endian = [];
            for (var i = 0; i < input.length; i += 2)
            {
                endian.push(input.substring(i, i + 2));
            }
            endian.reverse();
            
            output = endian.join("");
        }
        output = parseInt(output, 16)
        this.idx += bytes * 2;
        //console.log("IDX: " + (this.idx / 2));
        return output;
    };
    this.str_read = function (bytes)    // read X bytes of world file data as string
    {
        var input = this.hex.substr(this.idx, bytes*2);
        var output = "";
        for (var i = 0; i < input.length; i += 2)
        {
            output += String.fromCharCode(parseInt(input.substring(i, i + 2), 16));
        }            
        this.idx += bytes * 2;
        //console.log("IDX: " + (this.idx / 2));
        return output;
    };
};

function pull_file()
{
    if ($(this).hasClass("selected"))
    {
        //$(this).find("ul").toggle();
        return false;
    }
    
    $("#file-list li").removeClass("selected");
    $(this).addClass("selected");
    var valid_extensions = ["Title Screen", "hi", "txt", "doc", "jpg", "gif", "bmp", "png", "bat", "zzt"];
    var filename = $(this).text();
    var split = filename.toLowerCase().split(".");
    var ext = split[split.length - 1];
    
    if (valid_extensions.indexOf(ext) == -1)
    {
        
        if (filename == "Title Screen")
        {
            $("#details").html('<img src="/assets/images/screenshots/no_screenshot.png">');
            return true;
        }
        else
        {
            $("#details").html(filename + " is not a supported filetype that can be viewed.");
            return false;
        }
    }
    
    $.ajax({
        url:"/ajax/get_zip_file", 
        data:{
            "letter":letter,
            "zip":zip,
            "filename":filename
        }
    }).done(function (data){
        if (ext == "zzt")
        {
            world = parse_world("zzt", data);
            
            // Write the board names to the file list
            var board_list = "<ul>";
            for (var x = 0; x < world.boards.length; x++)
            {
                board_list += "<li class='board' data-board-number='"+x+"'>"+world.boards[x].name+"</li>";
            }
            board_list += "</ul>";
            $("#file-list li.selected").append(board_list + "<br>");
            $("li.board").click(render_board); // Bind event
        }
        else
        {
            $("#details").html(data);
            $("#filename").text(filename);
        }
    });
}

function parse_world(type, data)
{
    if (type != "zzt")
    {
        $("#details").html("I can't render this");
        return false;
    }
    
    // ZZT World Parsing
    var world = new World(data);
    
    // Parse World Bytes
    world.world_bytes = world.read(2);
    //console.log("World Bytes     : " + world.world_bytes);
    
    if (world.world_bytes != 65535)
    {
        $("#details").html("World is not a valid ZZT world");
        return false;
    }
    
    // Parse Number of Boards (this starts at 0 for a title screen only)
    world.board_count = world.read(2);
    //console.log("Boards          : " + world.board_count);
    
    // Parse World Stats
    world.ammo = world.read(2)
    world.gems = world.read(2)
    world.keys = world.read(7) // This one is special
    world.health = world.read(2);
    world.starting_board = world.read(2);
    
    /*
    console.log("Ammo            : " + world.ammo);
    console.log("Gems            : " + world.gems);
    console.log("Keys            : " + world.keys);
    console.log("Health          : " + world.health);
    console.log("Starting board  : " + world.starting_board);
    */
    
    // Begin Parse ZZT Specific World Stats
    world.torches = world.read(2);
    world.torch_cycles = world.read(2);
    world.energizer_cycles = world.read(2);
    world.read(2); // Unused bytes
    world.score = world.read(2);
    world.name_length = world.read(1);
    world.name = world.str_read(20).substr(0,world.name_length);
    
    /*
    console.log("Torches         : " + world.torches);
    console.log("T Cycles        : " + world.torch_cycles);
    console.log("E Cycles        : " + world.energizer_cycles);
    console.log("Score           : " + world.score);
    console.log("Name Length     : " + world.name_length);
    console.log("Name            : " + world.name);
    */
    
    // Parse Flags
    for (var x = 0; x < 10; x++)
    {
        var len = world.read(1);                              // Read flag length
        //console.log("Flag " + x + " length is " + len);
        world.flags.push(world.str_read(20).substr(0,len));   // Read flag name
    }
    
    world.time_passed = world.read(2);
    world.read(2)                       // Unused playerdata
    world.save = (world.read(1) != 0);  // Save/Lock file
    
    //console.log("Flags           : " + world.flags);
    //console.log("Save            : " + world.save);
    // End Parse ZZT Specific World Stats
    
    // Begin Parse SZZT Specific World Stats
    // TODO: This is extremely low priority.
    // End Parse SZZT Specific World Stats
    
    // Parse Boards
    world.idx = 1024; // todo: debug, this shouldn't be necessary at all
    for (var x = 0; x <= world.board_count; x++)
    {
        world.boards.push(parse_board(world));
    }
    
    console.log("ALL BOARDS PARSED!!!");
    return world;
}

function parse_board(world)
{
    var board = {};
    board.room = [];
    board.size = world.read(2);
    board.name_length = world.read(1);
    board.name = world.str_read(50).substr(0,board.name_length);
    //console.log("Size: " + board.size);
    //console.log("Name: " + board.name);
    
    // Parse Elements
    var parsed_tiles = 0;
    
    while (parsed_tiles < 1500)
    {
        var quantity = world.read(1);
        var element_id = world.read(1);
        var color = world.read(1);
        board.room.push([quantity, element_id, color]);
        //$("#debug").val($("#debug").val() + "\n" + quantity + " " + colors[color % 16] + " on " + colors[parseInt(color / 16)] + " " + elements[element_id]);
        parsed_tiles += quantity;
    }
    
    // Parse Properties
    board.max_shots = world.read(1);
    board.dark = world.read(1);
    board.exit_north = world.read(1);
    board.exit_south = world.read(1);
    board.exit_west = world.read(1);
    board.exit_east = world.read(1);
    board.zap = world.read(1);
    board.message_length = world.read(1);
    board.message = world.str_read(58).substr(0,board.message_length);
    board.enter_x = world.read(1);
    board.enter_y = world.read(1);
    board.time_limit = world.read(2);
    world.read(16); // Padding
    board.stat_count = world.read(2);
    board.stats = [];
    // Super ZZT Properties
    // End
    
    // Parse Stats
    var parsed_stats = 0;
    
    while (parsed_stats <= board.stat_count)
    {
        var stat = {};
        stat.x = world.read(1);
        stat.y = world.read(1);
        stat.x_step = world.read(2);
        stat.y_step = world.read(2);
        stat.cycle = world.read(2);
        stat.param1 = world.read(1);
        stat.param2 = world.read(1);
        stat.param3 = world.read(1);
        stat.follower = world.read(2);
        stat.leader = world.read(2);
        stat.under_id = world.read(1);
        stat.under_color = world.read(1);
        stat.pointer = world.read(4);
        stat.oop_idx = world.read(2);
        stat.oop_length = world.read(2);
        world.read(8); // Padding
        
        if (stat.oop_length > 32767) // Pre-bound element
            stat.oop_length = 0;
            
        if (stat.oop_length)
        {
            stat.oop = world.str_read(stat.oop_length);
        }
        else
        {
            stat.oop = "";
        }
        
        board.stats.push(stat);
        parsed_stats++;
    }
    
    return board;
}

function render_board()
{
    var board_number = $(this).data("board-number");
    $("#details").html("<canvas id='world-canvas' width='480' height='350'>Your browser is outdated and does not support the canvas element.</canvas>");
    var canvas = document.getElementById("world-canvas");
    var ctx = canvas.getContext("2d");
    
    // Get tiles
    var tiles = world.boards[board_number];
    var x = 0;
    var y = 0;
    for (var chunk_idx = 0; chunk_idx < tiles.room.length; chunk_idx++)
    {
        var chunk = tiles.room[chunk_idx];
        /*
        console.log("QTY:" + chunk[0]);
        console.log("ELE:" + chunk[1]);
        console.log("CLR:" + chunk[2]);
        */
        
        for (qty = 0; qty < chunk[0]; qty++)
        {
            print(ctx, characters[chunk[1]], chunk[2], x, y);
            x += 1;
            if (x > 59)
            {
                x = 0;
                y += 1;
            }
        }
    }
}

$(document).ready(function (){
    $("#file-list li").click(pull_file);
});

/* Canvas Functions */
function print(ctx, character, color, x, y)
{
    var image = document.getElementById("ascii");
    var ch_x = character % 16;
    var ch_y = parseInt(character / 16);
    var bg = colors[parseInt(color / 16)];
    var fg = colors[color % 16];
    
    // Background
    
    ctx.fillStyle = bg;
    ctx.fillRect(x*8, y*14, 8, 14);
    ctx.restore();
    
    // Draw the tile (it will be white by default)
    //ctx.drawImage(image, ch_x*8, ch_y*14, 8, 14, x*8, y*14, 8, 14 ); // 8x14
    
    
    // Foreground -- SLOW
    /*
    if (fg != 15)
    {
        var image_data = ctx.getImageData(x*8,y*14,8,14);
        var data = image_data.data;
        for (var i = 0; i < data.length; i += 4)
        {
            if (data[i] == 255 && data[i+1] == 255 && data[i+2] == 255)
            {
                data[i] = parseInt(fg.substr(1,2), 16); // red
                data[i+1] = parseInt(fg.substr(3,2), 16); // green
                data[i+2] = parseInt(fg.substr(5,2), 16); // blue
            }
        }
        ctx.putImageData(image_data, x*8, y*14);
        
    }
    */
    
    // Creates transparency for foreground
    ctx.globalCompositeOperation = "xor";
    ctx.drawImage(image, ch_x*8, ch_y*14, 8, 14, x*8, y*14, 8, 14 ); // 8x14
    // Draws foreground
    ctx.globalCompositeOperation = "destination-over";
    ctx.fillStyle = fg;
    ctx.fillRect(x*8, y*14, 8, 14);
    ctx.restore();
    
}
/* End Canvas Functions */