"use strict";
var elements = ["Empty", "Board Edge", "Messenger", "Monitor", "Player", "Ammo", "Torch", "Gem", "Key", "Door", "Scroll", "Passage", "Duplicator", "Bomb", "Energizer", "Star", "Conveyor, Clockwise", "Conveyor, Counterclockwise", "Bullet", "Water", "Forest", "Solid Wall", "Normal Wall", "Breakable Wall", "Boulder", "Slider, North-South", "Slider, East-West", "Fake Wall", "Invisible Wall", "Blink Wall", "Transporter", "Line Wall", "Ricochet", "Blink Ray, Horizontal", "Bear", "Ruffian", "Object", "Slime", "Shark", "Spinning Gun", "Pusher", "Lion", "Tiger", "Blink Ray, Vertical", "Centipede Head", "Centipede Segment", "Text, Blue", "Text, Green", "Text, Cyan", "Text, Red", "Text, Purple", "Text, Brown", "Text, Black"];
var colors = ["#000000", "#0000AA", "#00AA00", "#00AAAA", "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA", "#555555", "#5555FF", "#55FF55", "#55FFFF", "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF"];
var COLOR_NAMES = ["Black", "Dark Blue", "Dark Green", "Dark Cyan", "Dark Red", "Dark Purple", "Dark Yellow", "Gray", "Dark Gray", "Blue", "Green", "Cyan", "Red", "Purple", "Yellow", "White"];
var characters = [32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 47, 47, 248, 176, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 62, 249, 42, 205, 153, 5, 2, 42, 94, 24, 16, 234, 227, 186, 233, 79, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63];
var line_characters = {"0000":249, "0001":181, "0010":198, "0011":205, "0100":210, "0101":187, "0110":201, "0111":203, "1000":208, "1001":188, "1010":200, "1011":202, "1100":186, "1101":185, "1110":204, "1111":206};
var world = null;
var board_number = null;

var CANVAS_WIDTH = 480;
var CANVAS_HEIGHT = 350;
var TILE_WIDTH = 8;
var TILE_HEIGHT = 14;

console.log("CANVAS DIMENSIONS", CANVAS_WIDTH, CANVAS_HEIGHT);

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
        var output = input;
        
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
    $("#file-list li ul").remove();
    $("#file-list li br").remove();
    $(this).addClass("selected");
    var valid_extensions = ["Title Screen", "hi", "txt", "doc", "jpg", "jpeg", "gif", "bmp", "png", "bat", "zzt", "cfg", "dat", "wav", "mp3", "ogg", "mid", "midi"];
    var filename = $(this).contents().filter(function(){ return this.nodeType == 3; })[0].nodeValue;
    var split = filename.toLowerCase().split(".");
    var ext = split[split.length - 1];
    
    if (valid_extensions.indexOf(ext) == -1)
    {
        if (filename == "Title Screen")
        {
            $("#details").html('<img src="'+$(this).data("img")+'">');
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
                board_list += "<li class='board' data-board-number='"+x+"'>"+world.boards[x].title+"</li>";
            }
            board_list += "</ul>";
            $("#file-list li.selected").append(board_list + "<br>");
            $("li.board").click(render_board); // Bind event
            
            // Auto Load board
            if (load_board != "")
                auto_load_board(load_board);
        }
        else if (ext == "hi")
        {
            var scores = parse_scores(data);
            var output = "<div class='high-scores'>Score &nbsp;Name<br>";
            output += "----- &nbsp;----------------------------------<br>";
            for (var idx in scores)
            {
                output += scores[idx].score + " &nbsp;" + scores[idx].name + "<br>";
            }
            output += "</div>";
            $("#details").html(output);
        }
        else if (["jpg", "jpeg", "gif", "bmp", "png"].indexOf(ext) != -1)
        {
            var zip_image = new Image();
            zip_image.src = data;
            $("#details").html("<img id='zip_image' alt='Zip file image'>");
            $("#zip_image").attr("src", "data:image/'"+ext+"';base64,"+data);
            
            
        }
        else if (["wav", "mp3", "ogg", "mid", "midi"].indexOf(ext) != -1)
        {
            // TODO: Make this actually work
            if (ext == "wav")
                var type = "audio/wav wav";
            else if (ext == "mp3")
                var type = "audio/mpeg mp3";
            else if (ext == "ogg")
                var type = "audio/ogg ogg";
            else
                var type = "application/octet-stream";
            console.log(data);
            
            var audio_buffer = null;
            var context = new AudioContext();
            context.decodeAudioData(data, function(buffer) { audio_buffer = buffer; });
            console.log("L#147");
            
            var source = context.createBufferSource(); // creates a sound source
            source.buffer = audio_buffer;                    // tell the source which sound to play
            source.connect(context.destination);       // connect the source to the context's destination (the speakers)
            source.start(0)
            
            //$("#details").html("<audio id='zip_audio' src='"+zip_audio_url+"'>Your browser does not support HTML5 audio</audio>");
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
    
    // Parse World Stats
    world.ammo = world.read(2)
    world.gems = world.read(2)
    world.keys = world.read(7) // This one is special
    world.health = world.read(2);
    world.starting_board = world.read(2);
    
    // Begin Parse ZZT Specific World Stats
    world.torches = world.read(2);
    world.torch_cycles = world.read(2);
    world.energizer_cycles = world.read(2);
    world.read(2); // Unused bytes
    world.score = world.read(2);
    world.name_length = world.read(1);
    world.name = world.str_read(20).substr(0,world.name_length);
    
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
    
    var output = "World format: " + type.toUpperCase() + "<br>";
    output += "World name: " + world.name + "<br>";
    output += "Health: " + world.health + "<br>";
    output += "Ammo: " + world.ammo + "<br>";
    output += "Torches: " + world.torches + "<br>";
    output += "Gems: " + world.gems + "<br>";
    output += "Keys: " + world.keys + "<br>";
    output += "Score: " + world.score + "<br>";
    
    output += "Torch cycles: " + world.torch_cycles + "<br>";
    output += "Energizer cycles: " + world.energizer_cycles + "<br>";
    output += "Time elapsed: " + world.time_passed + "<br>";
    output += "Saved game: " + (world.save ? "Yes" : "No") + "<br>";
    
    for (var idx in world.flags)
    {
        if (world.flags[idx])
            output += "Flag "+idx+": " + world.flags[idx] + "<br>";
    }
    
    
    $("#world-info").html(output);
    return world;
}

function parse_board(world)
{
    var board = {};
    board.room = []; // Room is used for generic rendering
    board.elements = []; // Elements are used for individual tiles
    board.size = world.read(2);
    board.title_length = world.read(1);
    board.title = world.str_read(50).substr(0,board.title_length);
    //console.log("Size: " + board.size);
    //console.log("Name: " + board.name);
    
    // Placeholder way to deal with invalid elements
    if (ZZT_ELEMENTS.length < 256)
    {
        while (ZZT_ELEMENTS.length < 256)
            ZZT_ELEMENTS.push(
                {
                "id":ZZT_ELEMENTS.length,
                "name":"Element " + ZZT_ELEMENTS.length,
                "oop_name":"",
                "character":63
                }
            );
    }
    
    // Parse Elements
    var parsed_tiles = 0;
    
    while (parsed_tiles < 1500)
    {
        var quantity = world.read(1);
        var element_id = world.read(1);
        var color = world.read(1);
        board.room.push([quantity, element_id, color]);
        
        for (var tile_idx = 0; tile_idx < quantity; tile_idx++)
        {
            //console.log("ELEMENT", element_id, board.title, tile_idx, ZZT_ELEMENTS[element_id]["name"]);
            board.elements.push(
                {
                    "id":element_id,
                    "tile":tile_idx,
                    "name":ZZT_ELEMENTS[element_id]["name"],
                    "character":characters[element_id], // This is the default character before any additional board/stat parsing
                    "color_id":color,
                    "foreground":color % 16,
                    "background":color / 16,
                    "foreground_name":COLOR_NAMES[color % 16],
                    "background_name":COLOR_NAMES[Math.floor(color / 16)]
                }
            );
        }
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
    board_number = $(this).data("board-number");
    $("li.board").removeClass("selected");
    $(this).addClass("selected");
    set_dimensions();
    $("#details").html("<canvas id='world-canvas' width='"+CANVAS_WIDTH+"' height='"+CANVAS_HEIGHT+"'>Your browser is outdated and does not support the canvas element.</canvas>");
    var canvas = document.getElementById("world-canvas");
    var ctx = canvas.getContext("2d");
    
    // Get board
    var board = world.boards[board_number];
    
    // Write board information
    var loaded_file = $("#file-list ul > li.selected").contents().filter(function(){ return this.nodeType == 3; })[0].nodeValue;
    var output = "";
    output += "Title: " + board.title + "<br>";
    output += "Can fire: " + board.max_shots + " shot"+((board.max_shots != 1) ? "s" : "")+".<br>";
    output += "Board is dark: " + (board.dark ? "Yes" : "No") + "<br>";
    if (board.exit_north)
    {
        output += "Board ↑: ";
        output += '<a href="?file='+loaded_file+'&board='+board.exit_north+'">'+board.exit_north + " - " + world.boards[board.exit_north].title +"</a>";
        output += "<br>";
    }
    else
        output += "Board ↑: None" + "<br>";
    if (board.exit_south)
    {
        output += "Board ↓: ";
        output += '<a href="?file='+loaded_file+'&board='+board.exit_south+'">'+board.exit_south + " - " + world.boards[board.exit_south].title +"</a>";
        output += "<br>";
    }
    else
        output += "Board ↓: None" + "<br>";
    if (board.exit_east)
    {
        output += "Board →: ";
        output += '<a href="?file='+loaded_file+'&board='+board.exit_east+'">'+board.exit_east + " - " + world.boards[board.exit_east].title +"</a>";
        output += "<br>";
    }
    else
        output += "Board →: None" + "<br>";
    if (board.exit_west)
    {
        output += "Board ←: ";
        output += '<a href="?file='+loaded_file+'&board='+board.exit_west+'">'+board.exit_west + " - " + world.boards[board.exit_west].title +"</a>";
        output += "<br>";
    }
    else
        output += "Board ←: None" + "<br>";
    
    output += "Re-enter when zapped: " + (board.zap ? "Yes" : "No") + "<br>";
    output += "Re-enter X: " + board.enter_x + "<br>";
    output += "Re-enter Y: " + board.enter_y + "<br>";
    output += "Time limit: " + (board.time_limit ? "None" : board.time_limit + " sec"+(board.time_limit != 1 ? "s" : "")+".") + "<br>";
    
    output += "Stat elements: " + (board.stat_count + 1) + "/151<br>";
    output += "Board size: " + (board.size + 2) + " bytes<br>"; // Extra two bytes are for the "size of board" bytes themselves. This is necessary to match KevEdit.
    if (board.message != "")
        output += "Message: " + board.message + "<br>";
    
    $("#world-info").html(output);
    
    
    var x = 0;
    var y = 0;
    var tile = 0;
    var line_walls = {}; // I am not happy with this solution
    var line_colors = {};
    for (var chunk_idx = 0; chunk_idx < board.room.length; chunk_idx++)
    {
        var chunk = board.room[chunk_idx];
        /*
        console.log("QTY:" + chunk[0]);
        console.log("ELE:" + chunk[1]);
        console.log("CLR:" + chunk[2]);
        */
        
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
            print(ctx, line_characters[line_key], line_colors[line_idx], line_idx % 60, parseInt(line_idx / 60));
        }
    }
    
    $("#world-canvas").click(stat_info);
    console.log(document.getElementById("world-canvas").toDataURL());
    
    // DEBUG Screenshot Saving
    /*
    if (save)
    {
        var canvas = document.getElementById("world-canvas");
        base64 = canvas.toDataURL();
        $("input[name=screenshot]").val(base64);
        $("form[name=save]")[0].submit();
    }
    */
    // END DEBUG
    return true;
}

function stat_info(e)
{
    var posX = $(this).offset().left;
    var posY = $(this).offset().top;
    var x = parseInt((e.pageX - posX) / TILE_WIDTH) + 1;
    var y = parseInt((e.pageY - posY) / TILE_HEIGHT) + 1;
    var tile_idx = ((y-1) * 60) + (x-1);
    var output = "";
    
    // General info
    var tile = world.boards[board_number].elements[tile_idx];
    output += "Coordinates: ("+x+", "+y+") [Tile "+(tile_idx+1)+"/1500]" + "<br>";
    output += "ID: " + tile.id + "<br>";
    output += "Name: " + tile.name + "<br>";
    output += "Character: " + tile.character + "<br>";
    output += "Color ID: " + tile.color_id + "<br>";
    output += "Color Name: " + tile.foreground_name + " on " + tile.background_name + "<br>";
    
    // Iterate over stat elements
    var stat = null;
    for (var stat_idx = 0; stat_idx < world.boards[board_number].stats.length; stat_idx++)
    {
        if (world.boards[board_number].stats[stat_idx].x == x && world.boards[board_number].stats[stat_idx].y == y)
        {
            stat = world.boards[board_number].stats[stat_idx];
            break;
        }
    }
    
    if (stat != null)
    {
        output += "Cycle: " + stat.cycle + "<br>";
        output += (ZZT_ELEMENTS[tile.id].hasOwnProperty("param1") ? ZZT_ELEMENTS[tile.id].param1 : "Param1") + ": " + stat.param1 + "<br>";
        output += (ZZT_ELEMENTS[tile.id].hasOwnProperty("param2") ? ZZT_ELEMENTS[tile.id].param2 : "Param2") + ": " + stat.param2 + "<br>";
        
        // Passages get a link and the board's proper name
        if (tile.name == "Passage")
        {
            var loaded_file = $("#file-list ul > li.selected").contents().filter(function(){ return this.nodeType == 3; })[0].nodeValue;
            output += (ZZT_ELEMENTS[tile.id].hasOwnProperty("param3") ? ZZT_ELEMENTS[tile.id].param3 : "Param3") + ": ";
            output += '<a href="?file='+loaded_file+'&board='+stat.param3+'">'+stat.param3 + " - " + world.boards[stat.param3].title +"</a>";
            output += "<br>";
        }
        else
            output += (ZZT_ELEMENTS[tile.id].hasOwnProperty("param3") ? ZZT_ELEMENTS[tile.id].param3 : "Param3") + ": " + stat.param3 + "<br>";
        
        if (ZZT_ELEMENTS[tile.id].hasOwnProperty("step"))
            output += ZZT_ELEMENTS[tile.id].step + "<br>"
        output += "X-Step: " + stat.x_step + "<br>";
        output += "Y-Step: " + stat.y_step + "<br>";
        output += "Leader: " + stat.leader + "<br>";
        output += "Follower: " + stat.follower + "<br>";
        output += "Under ID: " + stat.under_id + "<br>";
        output += "Under Color: " + stat.under_color + "<br>";
        output += "Current Instruction: " + stat.oop_idx + "<br>";
        output += "OOP Length: " + stat.oop_length + "<br>";
        if (stat.oop_length > 0)
        {
            output += "================ ZZT-OOP =================<br>";
            output += stat.oop.replace(/\r/g, "<br>");
        }
    }
    
    $("#world-info").html(output);
    
    return true;
}

$(document).ready(function (){
    $("#file-list li").click(pull_file);
    
    if (load_file)
    {
        auto_load();
    }
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
    ctx.fillRect(x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT);
    ctx.restore();
    
    // Creates transparency for foreground
    ctx.globalCompositeOperation = "xor";
    ctx.drawImage(image, ch_x*TILE_WIDTH, ch_y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT, x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT);
    // Draw foreground
    ctx.globalCompositeOperation = "destination-over";
    ctx.fillStyle = fg;
    ctx.fillRect(x*TILE_WIDTH, y*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT);
    ctx.restore();
    return true;
}
/* End Canvas Functions */

/* Auto Load functions */
function auto_load()
{
    $("#file-list li").each(function (){
        if ($(this).text() == load_file)
        {
            $(this).click();
            return true;
        }
    });
}

function auto_load_board(load_board)
{
    $("li.board").each(function (){
        if ($(this).data("board-number") == load_board)
        {
            $(this).click();
            return true;
        }
    });
}
/* End Auto Load Functions */

function parse_scores(data)
{
    var scores = [];
    var idx = 0;
    while (true)
    {
        // Read the first byte for length of name
        var name_length = read(data, 1, idx);
        idx += 2;
        
        if (name_length == 0)
            break;
        
        var name = str_read(data, 50, idx).substr(0,name_length);
        idx += 100;
        
        var score = read(data, 2, idx);
        idx += 4;
        
        scores.push({"name":name, "score":score});
    }
    return scores;
}

function read(data, bytes, idx)
{
    var input = data.substr(idx, bytes*2);
    var output = input;
    
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
    return output;
}

function str_read(data, bytes, idx)
{
    var input = data.substr(idx, bytes*2);
    var output = "";
    for (var i = 0; i < input.length; i += 2)
    {
        output += String.fromCharCode(parseInt(input.substring(i, i + 2), 16));
    }
    return output;
};

function set_dimensions()
{
    CANVAS_WIDTH = $("#ascii").get(0).width / 16 * 60;
    CANVAS_HEIGHT = $("#ascii").get(0).height / 16 * 25;
    
    TILE_WIDTH = CANVAS_WIDTH / 60;
    TILE_HEIGHT = CANVAS_HEIGHT / 25;
}

function str_read(data, bytes, idx)
{
    var input = data.substr(idx, bytes*2);
    var output = "";
    for (var i = 0; i < input.length; i += 2)
    {
        output += String.fromCharCode(parseInt(input.substring(i, i + 2), 16));
    }
    return output;
};