"use strict";
var elements = ["Empty", "Board Edge", "Messenger", "Monitor", "Player", "Ammo", "Torch", "Gem", "Key", "Door", "Scroll", "Passage", "Duplicator", "Bomb", "Energizer", "Star", "Conveyor, Clockwise", "Conveyor, Counterclockwise", "Bullet", "Water", "Forest", "Solid Wall", "Normal Wall", "Breakable Wall", "Boulder", "Slider, North-South", "Slider, East-West", "Fake Wall", "Invisible Wall", "Blink Wall", "Transporter", "Line Wall", "Ricochet", "Blink Ray, Horizontal", "Bear", "Ruffian", "Object", "Slime", "Shark", "Spinning Gun", "Pusher", "Lion", "Tiger", "Blink Ray, Vertical", "Centipede Head", "Centipede Segment", "Text, Blue", "Text, Green", "Text, Cyan", "Text, Red", "Text, Purple", "Text, Brown", "Text, Black"];
var colors = ["#000000", "#0000AA", "#00AA00", "#00AAAA", "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA", "#555555", "#5555FF", "#55FF55", "#55FFFF", "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF"];
var COLOR_NAMES = ["Black", "Dark Blue", "Dark Green", "Dark Cyan", "Dark Red", "Dark Purple", "Dark Yellow", "Gray", "Dark Gray", "Blue", "Green", "Cyan", "Red", "Purple", "Yellow", "White"];
var characters = [32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 47, 47, 248, 176, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 62, 249, 42, 205, 153, 5, 2, 42, 94, 24, 16, 234, 227, 186, 233, 79, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63];
var line_characters = {"0000":249, "0001":181, "0010":198, "0011":205, "0100":210, "0101":187, "0110":201, "0111":203, "1000":208, "1001":188, "1010":200, "1011":202, "1100":186, "1101":185, "1110":204, "1111":206};

var CP437_TO_UNICODE = {
    0:0,
    1:9786,
    2:9787,
    3:9829,
    4:9830,
    5:9827,
    6:9824,
    7:8226,
    8:9688,
    9:9675,
    10:9689,
    11:9794,
    12:9792,
    13:9834,
    14:9835,
    15:9788,
    16:9658,
    17:9668,
    18:8597,
    19:8252,
    20:182,
    21:167,
    22:9644,
    23:8616,
    24:8593,
    25:8595,
    26:8594,
    27:8592,
    28:8735,
    29:8596,
    30:9650,
    31:9660,
    32:32,
    33:33,
    34:34,
    35:35,
    36:36,
    37:37,
    38:38,
    39:39,
    40:40,
    41:41,
    42:42,
    43:43,
    44:44,
    45:45,
    46:46,
    47:47,
    48:48,
    49:49,
    50:50,
    51:51,
    52:52,
    53:53,
    54:54,
    55:55,
    56:56,
    57:57,
    58:58,
    59:59,
    60:60,
    61:61,
    62:62,
    63:63,
    64:64,
    65:65,
    66:66,
    67:67,
    68:68,
    69:69,
    70:70,
    71:71,
    72:72,
    73:73,
    74:74,
    75:75,
    76:76,
    77:77,
    78:78,
    79:79,
    80:80,
    81:81,
    82:82,
    83:83,
    84:84,
    85:85,
    86:86,
    87:87,
    88:88,
    89:89,
    90:90,
    91:91,
    92:92,
    93:93,
    94:94,
    95:95,
    96:96,
    97:97,
    98:98,
    99:99,
    100:100,
    101:101,
    102:102,
    103:103,
    104:104,
    105:105,
    106:106,
    107:107,
    108:108,
    109:109,
    110:110,
    111:111,
    112:112,
    113:113,
    114:114,
    115:115,
    116:116,
    117:117,
    118:118,
    119:119,
    120:120,
    121:121,
    122:122,
    123:123,
    124:124,
    125:125,
    126:126,
    127:8962,
    128:199,
    129:252,
    130:233,
    131:226,
    132:228,
    133:224,
    134:229,
    135:231,
    136:234,
    137:235,
    138:232,
    139:239,
    140:238,
    141:236,
    142:196,
    143:197,
    144:201,
    145:230,
    146:198,
    147:244,
    148:246,
    149:242,
    150:251,
    151:249,
    152:255,
    153:214,
    154:220,
    155:162,
    156:163,
    157:165,
    158:8359,
    159:402,
    160:225,
    161:237,
    162:243,
    163:250,
    164:241,
    165:209,
    166:170,
    167:186,
    168:191,
    169:8976,
    170:172,
    171:189,
    172:188,
    173:161,
    174:171,
    175:187,
    176:9617,
    177:9618,
    178:9619,
    179:9474,
    180:9508,
    181:9569,
    182:9570,
    183:9558,
    184:9557,
    185:9571,
    186:9553,
    187:9559,
    188:9565,
    189:9564,
    190:9563,
    191:9488,
    192:9492,
    193:9524,
    194:9516,
    195:9500,
    196:9472,
    197:9532,
    198:9566,
    199:9567,
    200:9562,
    201:9556,
    202:9577,
    203:9574,
    204:9568,
    205:9552,
    206:9580,
    207:9575,
    208:9576,
    209:9572,
    210:9573,
    211:9561,
    212:9560,
    213:9554,
    214:9555,
    215:9579,
    216:9578,
    217:9496,
    218:9484,
    219:9608,
    220:9604,
    221:9612,
    222:9616,
    223:9600,
    224:945,
    225:223,
    226:915,
    227:960,
    228:931,
    229:963,
    230:181,
    231:964,
    232:934,
    233:920,
    234:937,
    235:948,
    236:8734,
    237:966,
    238:949,
    239:8745,
    240:8801,
    241:177,
    242:8805,
    243:8804,
    244:8992,
    245:8993,
    246:247,
    247:8776,
    248:176,
    249:8729,
    250:183,
    251:8730,
    252:8319,
    253:178,
    254:9632,
    255:160,
}

var world = null;
var board_number = null;

var canvas = null;
var ctx = null;
var filename = null;
var CHARSET_IMAGE = null;
var CHARSET_NAME = null;
var CANVAS_WIDTH = 480;
var CANVAS_HEIGHT = 350;
var TILE_WIDTH = 8;
var TILE_HEIGHT = 14;
var renderer = new Renderer();
renderer.render = renderer[$("select[name=renderer]").val()];

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
            var cp437_byte = parseInt(input.substring(i, i + 2), 16);
            // convert CP437 to unicode
            var unicode_ch = String.fromCharCode(CP437_TO_UNICODE[cp437_byte]);
            // Since this is text and not graphics, ♪ must be made a carraige return
            if (unicode_ch == "♪")
                unicode_ch = "\r";
            output += unicode_ch;
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
    var valid_extensions = ["Title Screen", "hi", "txt", "doc", "jpg", "jpeg", "gif", "bmp", "png", "bat", "zzt", "cfg", "dat", "wav", "mp3", "ogg", "mid", "midi", "nfo", "com"];
    filename = $(this).contents().filter(function(){ return this.nodeType == 3; })[0].nodeValue;
    var split = filename.toLowerCase().split(".");
    var head = split[0];
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

    // Add to history
    var state = {"load_file": filename, "load_board":"", "tab":""};
    var qs = "?file=" + filename + window.location.hash;
    if (! history.state || (history.state["load_file"] != filename))
    {
        history.pushState(state, "", qs);
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
        else if (ext == "com")
        {
            // Load the font
            $("select[name=charset]").val(head);

            // Display the font
            $("#details").html("<img src='/static/images/charsets/"+head+".png' class='charset' alt='"+head+"' title='"+head+"'>");
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
    world.idx = 1024;
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
    var start_idx = world.idx;
    var procced_bytes = 0;
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
        procced_bytes += 3;
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
    var oop_read = 0;

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
            oop_read += stat.oop_length;

            // Escape HTML
            stat.oop = stat.oop.replace("<", "&lt;");
            stat.oop = stat.oop.replace(">", "&gt;");
        }
        else
        {
            stat.oop = "";
        }

        board.stats.push(stat);

        parsed_stats++;
    }

    // Jump to the start of the next board in file (for corrupt boards)
    var manual_idx = (start_idx + board.size * 2) + 4;
    if (world.idx != manual_idx)
    {
		board.corrupt = true;
		world.idx = manual_idx;
	}
    return board;
}

function render_board()
{
    board_number = $(this).data("board-number");
    $("li.board").removeClass("selected");
    $(this).addClass("selected");
    load_charset();

    // Add to history
    var state = {"load_file": filename, "load_board":board_number, "tab":""};
    var qs = "?file=" + filename + "&board=" + board_number;
    if (! history.state || (history.state["load_board"] != board_number))
    {
        history.pushState(state, "", qs);
    }

    // Get board
    var board = world.boards[board_number];

    // Write board information
    var loaded_file = $("#file-list ul > li.selected").contents().filter(function(){ return this.nodeType == 3; })[0].nodeValue;
    var output = "";

    if (board.corrupt)
    {
		output += "<div class='error'>This board is corrupt</div>";
		$("#board-info").html(output);
		tab_select("board-info");
		return true;
	}

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
    render_stat_list(board);
    return true;
}

function draw_board()
{
    console.log("DRAWING A BOARD");
    ctx.globalCompositeOperation = "source-over";
    ctx.fillstyle = "black";
    ctx.fillRect(0,0,CANVAS_WIDTH,CANVAS_HEIGHT);
    var board_number = $(".board.selected").data("board-number");
    if (board_number == null)
        return false;

    var board = world.boards[board_number];

    renderer.render(board);

    $("#world-canvas").click(stat_info);

    // Click coordinates in hash
    if (hash_coords)
    {
        console.log("Auto clicking element...", hash_coords);
        var sliced = hash_coords.slice(1);
        var split = sliced.split(",");
        var e = {"data":{"x":split[0], "y":split[1]}};
        stat_info(e);
    }


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
    var hash_coords = "#" + x + "," + y;
    //window.location.hash = ;
    history.replaceState(undefined, undefined, hash_coords)
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
            output += "<code class='zzt-oop'>" + syntax_highlight(stat.oop) + "</code>";
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
    $("select[name=renderer]").change(function (){
        renderer.render = renderer[$(this).val()];
        $("li.selected.board").click();
        $("li[name=preferences]").click();
    });

    // Invisibles
    $("select[name=invisibles]").change(function (){
        renderer.invisible_style = $(this).val();
        renderer.render(world.boards[board_number]);
    });

    // High Intensity BGs
    $("select[name=intensity]").change(function (){
        renderer.bg_intensity = $(this).val();
        renderer.render(world.boards[board_number]);
    });

    // Keyboard Shortcuts
    $(window).keyup(function (e){
        if ($("input[name=q]").is(":focus"))
            return false;

        if (e.keyCode == 107 || e.keyCode == 61 || e.keyCode == 74) // Next Board
            $("li.board.selected").next().click()
        else if (e.keyCode == 109 || e.keyCode == 173 || e.keyCode == 75) // Previous Board
            $("li.board.selected").prev().click()
    });

    // History
    $(window).bind("popstate", function(e) {
        console.log("POPSTATE", history.state);
        console.log("FILENAME CURRENT", filename);
        console.log("BOARD CURRENT", board_number);
        if (history.state)
        {
            load_file = history.state["load_file"];
            load_board = history.state["load_board"];

            if (filename != load_file)
            {
                console.log("Clicking new file", load_file);
                auto_load();
            }

            if (board_number != load_board && load_board)
            {
                console.log("Clicking new board", load_board);
                $("li.board[data-board-number="+load_board+"]").click();
            }
        }
    });

    if (load_file)
    {
        auto_load();
    }
});

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

    if ($("#world-canvas").length == 0)
        var no_canvas = true;
    else
        var no_canvas = false;

    // Charset needs to be loaded and/or canvas doesn't exist
    if (CHARSET_NAME != selected_charset || no_canvas)
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

function syntax_highlight(oop)
{
        var oop = oop.split("\r");
        for (var idx in oop)
        {
            // Symbols: @, #, /, ?, :, ', !, $
            if (idx == 0 && oop[idx][0] && oop[idx][0] == "@")
                oop[idx] = "<span class='name'>@</span><span class='yellow'>" + oop[idx].slice(1) + "</span>";
            else if (oop[idx][0] && oop[idx][0] == "#")
            {
                oop[idx] = "<span class='command'>#</span>" + oop[idx].slice(1);
            }
            else if (oop[idx][0] && oop[idx][0] == "/")
            {
                oop[idx] = oop[idx].replace(/\//g, "<span class='go'>/</span>");
            }
            else if (oop[idx][0] && oop[idx][0] == "?")
            {
                oop[idx] = oop[idx].replace(/\?/g, "<span class='try'>?</span>");
            }
            else if (oop[idx][0] && oop[idx][0] == ":")
            {
                oop[idx] = "<span class='label'>:</span><span class='orange'>" + oop[idx].slice(1) + "</span>";
            }
            else if (oop[idx][0] && oop[idx][0] == "'")
            {
                oop[idx] = "<span class='comment'>'" + oop[idx].slice(1) + "</span>"    ;
            }
            else if (oop[idx][0] && oop[idx][0] == "!")
            {
                oop[idx] = "<span class='hyperlink'>!</span><span class='label'>" +
                    oop[idx].slice(1, oop[idx].indexOf(";")) +
                    "</span><span class='hyperlink'>;</span>" +
                    oop[idx].slice(oop[idx].indexOf(";")+1);
            }
            else if (oop[idx][0] && oop[idx][0] == "$")
            {
                oop[idx] = "<span class='center'>$</span><span class=''>" + oop[idx].slice(1) + "</span>";
            }
        }
        return oop.join("\n");
}

function render_stat_list(board)
{
    var stat_list = "<a id='stat-toggle' class='jsLink'>Toggle Codeless Stats</a>\n";
    stat_list += "<ol>\n";
    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
    {
        var stat = board.stats[stat_idx];
        var stat_name = board.elements[stat.tile_idx].name;
        if ((stat_name == "Scroll" || stat_name == "Object") && stat.oop[0] == "@")
            stat_name = stat.oop.slice(0, stat.oop.indexOf("\r"));

        if (stat.oop.length == 0)
            stat_list += "<li class='empty'>";
        else
            stat_list += "<li>";
        stat_list += "<a class='jsLink' name='stat-link' data-x='"+stat.x+"' data-y='"+stat.y+"'>";
        stat_list +="("+ ("00"+stat.x).slice(-2) +", "+ ("00"+stat.y).slice(-2) +") ["+(("0000"+(stat.tile_idx+1)).slice(-4))+"] "
        stat_list += stat_name+"</a> "+ stat.oop.length +" bytes</li>\n";
    }
    stat_list += "</ol>\n";
    $("#stat-info").html(stat_list);
    $("a[name=stat-link]").click(function (){
        var e = {"data":{"x":$(this).data("x"), "y":$(this).data("y")}};
        stat_info(e);
    });

    $("#stat-toggle").click(function (){
        if ($(this).hasClass("activated")) // Redisplay
            $("#stat-info li.empty").css({"visibility": "visible", "height":"auto"});
        else // Hide
            $("#stat-info li.empty").css({"visibility": "hidden", "height":0});
        $(this).toggleClass("activated");

    });
    return true;
}

/* DEBUG FUNCTION */
function debug_file(file)
{
    $.ajax({
        url:"/ajax/debug_file?file="+file,
        data:{}
    }).done(function (data){
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
    });
}
