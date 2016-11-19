"use strict";
var elements = ["Empty", "Board Edge", "Messenger", "Monitor", "Player", "Ammo", "Torch", "Gem", "Key", "Door", "Scroll", "Passage", "Duplicator", "Bomb", "Energizer", "Star", "Conveyor, Clockwise", "Conveyor, Counterclockwise", "Bullet", "Water", "Forest", "Solid Wall", "Normal Wall", "Breakable Wall", "Boulder", "Slider, North-South", "Slider, East-West", "Fake Wall", "Invisible Wall", "Blink Wall", "Transporter", "Line Wall", "Ricochet", "Blink Ray, Horizontal", "Bear", "Ruffian", "Object", "Slime", "Shark", "Spinning Gun", "Pusher", "Lion", "Tiger", "Blink Ray, Vertical", "Centipede Head", "Centipede Segment", "Text, Blue", "Text, Green", "Text, Cyan", "Text, Red", "Text, Purple", "Text, Brown", "Text, Black"];
var colors = ["#000000", "#0000AA", "#00AA00", "#00AAAA", "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA", "#555555", "#5555FF", "#55FF55", "#55FFFF", "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF"];
var COLOR_NAMES = ["Black", "Dark Blue", "Dark Green", "Dark Cyan", "Dark Red", "Dark Purple", "Dark Yellow", "Gray", "Dark Gray", "Blue", "Green", "Cyan", "Red", "Purple", "Yellow", "White"];
var characters = [32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 47, 47, 248, 176, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 62, 249, 42, 205, 153, 5, 2, 42, 94, 24, 16, 234, 227, 186, 233, 79, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63];
var line_characters = {"0000":249, "0001":181, "0010":198, "0011":205, "0100":210, "0101":187, "0110":201, "0111":203, "1000":208, "1001":188, "1010":200, "1011":202, "1100":186, "1101":185, "1110":204, "1111":206};
var world = null;
var board_number = null;

var canvas = null;
var ctx = null;
var CHARSET_IMAGE = null;
var CHARSET_NAME = null;
var CANVAS_WIDTH = 480;
var CANVAS_HEIGHT = 350;
var TILE_WIDTH = 8;
var TILE_HEIGHT = 14;
var renderer = new Renderer();
renderer.render = renderer[$("input[name=renderer]").filter(":checked").val()];

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
    var valid_extensions = ["Title Screen", "hi", "txt", "doc", "jpg", "jpeg", "gif", "bmp", "png", "bat", "zzt", "cfg", "dat", "wav", "mp3", "ogg", "mid", "midi", "nfo"];
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
                board_list += "<li class='board' data-board-number='"+x+"'>"+(world.boards[x].title ? world.boards[x].title : "-untitled")+"</li>";
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
    output += "Number of Boards: " + (world.board_count + 1) + "<br>";
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
    tab_select("world-info");
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

    // Placeholder way to deal with invalid elements
    if (ZZT_ELEMENTS.length < 256)
    {
        while (ZZT_ELEMENTS.length < 256)
            ZZT_ELEMENTS.push(
                {
                "id":ZZT_ELEMENTS.length,
                "name":"Unknown Element " + ZZT_ELEMENTS.length,
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
        stat.tile_idx = ((stat.y-1) * 60) + (stat.x-1);
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
    load_charset();

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

    $("#board-info").html(output);
    tab_select("board-info");

    // Render the stat info as well
    var stat_list = "<ul>\n"
    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
    {
        var stat = board.stats[stat_idx];
        var stat_name = board.elements[stat.tile_idx].name;
        if ((stat_name == "Scroll" || stat_name == "Object") && stat.oop[0] == "@")
            stat_name = stat.oop.slice(0, stat.oop.indexOf("\r"));

        stat_list += "<li><a class='jsLink' name='stat-link' data-x='"+stat.x+"' data-y='"+stat.y+"'>("+ ("00"+stat.x).slice(-2) +", "+ ("00"+stat.y).slice(-2) +") ["+(("0000"+(stat.tile_idx+1)).slice(-4))+"] "+stat_name+"</a></li>\n";
    }
    stat_list += "</ul>\n";
    $("#stat-info").html(stat_list);
    $("a[name=stat-link]").click(function (){
        var e = {"data":{"x":$(this).data("x"), "y":$(this).data("y")}};
        stat_info(e);
    });
    return true;
}

function draw_board()
{
    ctx.globalCompositeOperation = "source-over";
    ctx.fillstyle = "black";
    ctx.fillRect(0,0,CANVAS_WIDTH,CANVAS_HEIGHT);
    var board_number = $(".board.selected").data("board-number");
    if (board_number == null)
        return false;

    var board = world.boards[board_number];

    renderer.render(board);
    
    $("#world-canvas").click(stat_info);
    //console.log(document.getElementById("world-canvas").toDataURL());

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
}

function stat_info(e)
{
    console.log(e.data);
    if (! e.data)
    {
        var posX = $(this).offset().left;
        var posY = $(this).offset().top;
        var x = parseInt((e.pageX - posX) / TILE_WIDTH) + 1;
        var y = parseInt((e.pageY - posY) / TILE_HEIGHT) + 1;
    }
    else
    {
        var x = e.data.x;
        var y = e.data.y;
    }
    var tile_idx = ((y-1) * 60) + (x-1);
    var output = "";

    // General info
    var tile = world.boards[board_number].elements[tile_idx];
    output += "Coordinates: ("+x+", "+y+") [Tile "+(tile_idx+1)+"/1500]" + "<br>";
    output += "ID: " + tile.id + "<br>";
    output += "Name: " + tile.name + "<br>";
    output += "Default Character: " + tile.character + "<br>";
    //output += "Color ID: " + tile.color_id + "<br>";
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
    
    $("#element-info").html(output);
    tab_select("element-info");

    return true;
}

function tab_select(selector)
{
    $("#world-info, #board-info, #element-info, #stat-info, #preferences").hide();
    $("li[name=world-info], li[name=board-info], li[name=element-info], li[name=preferences], li[name=stat-info]").removeClass("selected");
    $("li[name="+selector+"]").addClass("selected");
    $("#"+selector).show();
}

$(document).ready(function (){
    $("#file-list li").click(pull_file);
    $("#file-tabs ul li").click(function (){tab_select($(this).attr("name"))});
    
    $("select[name=charset]").change(load_charset);
    $("input[name=2x]").change(load_charset);
    
    // Renderer
    $("input[name=renderer]").change(function (){
        console.log("Hello?");
        renderer.render = renderer[$(this).filter(":checked").val()];
        $("li.selected.board").click();
        $("li[name=preferences]").click();
    });
    
    // Keyboard Shortcuts
    $(window).keyup(function (e){
        if (e.keyCode == 107 || e.keyCode == 61) // Next
            $("li.board.selected").next().click()
        else if (e.keyCode == 109 || e.keyCode == 173) // Prev
            $("li.board.selected").prev().click()
    });

    if (load_file)
    {
        auto_load();
    }
});

/* Canvas Functions */
function print(ctx, character, color, x, y)
{
    var ch_x = character % 16;
    var ch_y = parseInt(character / 16);
    var bg = colors[parseInt(color / 16)];
    var fg = colors[color % 16];

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

function load_charset()
{
    var selected_charset = $("select[name=charset]").val() + ($("input[name=2x]").prop("checked") ? "-2x" : "");

    // Charset needs to be loaded
    if (CHARSET_NAME != selected_charset)
    {
        CHARSET_NAME = selected_charset;
        CHARSET_IMAGE = new Image();
        CHARSET_IMAGE.src = "/static/images/charsets/"+CHARSET_NAME+".png";
        CHARSET_IMAGE.addEventListener("load", function (){
            CANVAS_WIDTH = CHARSET_IMAGE.width / 16 * 60;
            CANVAS_HEIGHT = CHARSET_IMAGE.height / 16 * 25;

            TILE_WIDTH = CANVAS_WIDTH / 60;
            TILE_HEIGHT = CANVAS_HEIGHT / 25;

            $("#details").html("<div id='overlay'></div><canvas id='world-canvas' width='"+CANVAS_WIDTH+"' height='"+CANVAS_HEIGHT+"'>Your browser is outdated and does not support the canvas element.</canvas>");
            canvas = document.getElementById("world-canvas");
            ctx = canvas.getContext("2d");

            draw_board();
        });
    }
    else
    {
        draw_board();
    }
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
