"use strict";
var colors = [
    "#000000", "#0000AA", "#00AA00", "#00AAAA",
    "#AA0000", "#AA00AA", "#AA5500", "#AAAAAA",
    "#555555", "#5555FF", "#55FF55", "#55FFFF",
    "#FF5555", "#FF55FF", "#FFFF55", "#FFFFFF"
];

var COLOR_NAMES = [
    "Black", "Dark Blue", "Dark Green", "Dark Cyan",
    "Dark Red", "Dark Purple", "Dark Yellow", "Gray",
    "Dark Gray", "Blue", "Green", "Cyan",
    "Red", "Purple", "Yellow", "White"
];

var line_characters = {
    "0000":249, "0001":181, "0010":198, "0011":205,
    "0100":210, "0101":187, "0110":201, "0111":203,
    "1000":208, "1001":188, "1010":200, "1011":202,
    "1100":186, "1101":185, "1110":204, "1111":206
};

var web_characters = {
    "0000":250, "0001":196, "0010":196, "0011":196,
    "0100":179, "0101":191, "0110":218, "0111":194,
    "1000":179, "1001":217, "1010":192, "1011":193,
    "1100":179, "1101":180, "1110":195, "1111":197
};
var ELEMENTS = null;
var ENGINE = null;

var engines = {
    "zzt":{
        "identifier": 0xFFFF,
        "max_world_length": 20,
        "max_flags": 10,
        "tile_count": 1500,
        "max_board_length": 50,
        "first_board_index": 1024,
        "board_width": 60,
        "board_height": 25,
        "elements": ["Empty", "Board Edge", "Messenger", "Monitor", "Player", "Ammo", "Torch", "Gem", "Key", "Door", "Scroll", "Passage", "Duplicator", "Bomb", "Energizer", "Star", "Conveyor, Clockwise", "Conveyor, Counterclockwise", "Bullet", "Water", "Forest", "Solid Wall", "Normal Wall", "Breakable Wall", "Boulder", "Slider, North-South", "Slider, East-West", "Fake Wall", "Invisible Wall", "Blink Wall", "Transporter", "Line Wall", "Ricochet", "Blink Ray, Horizontal", "Bear", "Ruffian", "Object", "Slime", "Shark", "Spinning Gun", "Pusher", "Lion", "Tiger", "Blink Ray, Vertical", "Centipede Head", "Centipede Segment", "Text, Blue", "Text, Green", "Text, Cyan", "Text, Red", "Text, Purple", "Text, Yellow", "Text, White"],
        "characters": [32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 179, 92, 248, 176, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 62, 249, 42, 205, 153, 5, 2, 42, 94, 24, 16, 234, 227, 186, 233, 79, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63]
        },
    "szt":{
        "identifier": 0xFFFE,
        "max_world_length": 20,
        "max_flags": 16,
        "tile_count": 7680,
        "max_board_length": 60,
        "first_board_index": 2048,
        "board_width": 96,
        "board_height": 80,
        "elements": ["Empty", "Board Edge", "Messenger", "Monitor", "Player", "Ammo", "Torch", "Gem", "Key", "Door", "Scroll", "Passage", "Duplicator", "Bomb", "Energizer", "Star", "Clockwise Conveyor", "Counter Clockwise Conveyor", "Bullet", "Lava", "Forest", "Solid Wall", "Normal Wall", "Breakable Wall", "Boulder", "Slider (NS)", "Slider (EW)", "Fake Wall", "Invisible Wall", "Blink Wall", "Transporter", "Line Wall", "Ricochet", "Horizontal Blink Ray", "Bear", "Ruffian", "Object", "Slime", "Shark", "Spinning Gun", "Pusher", "Lion", "Tiger", "Vertical Blink Ray", "Head", "Segment", "Element 46", "Floor", "Water N", "Water S", "Water W", "Water E", "Element 52", "Element 53", "Element 54", "Element 55", "Element 56", "Element 57", "Element 58", "Roton", "Dragon Pup", "Pairer", "Spider", "Web", "Stone", "Element 65", "Element 66", "Element 67", "Element 68", "Bullet", "Horizontal Blink Ray", "Vertical Blink Ray", "Star", "Blue Text", "Green Text", "Cyan Text", "Red Text", "Purple Text", "Yellow Text", "White Text"],
        "characters": [32, 32, 32, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 83, 47, 92, 248, 111, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 32, 206, 42, 205, 235, 5, 2, 42, 94, 24, 31, 234, 227, 186, 233, 79, 32, 176, 30, 31, 17, 16, 32, 32, 32, 32, 32, 32, 32, 148, 237, 229, 15, 197, 90, 32, 32, 32, 32, 248, 205, 186, 83, 32, 32, 32, 32, 32, 32, 32]
        }
};

var CP437_TO_UNICODE = {
    0:0, 1:9786,  2:9787, 3:9829, 4:9830, 5:9827, 6:9824, 7:8226,
    8:9688, 9:9675, 10:9689, 11:9794, 12:9792, 13:9834, 14:9835, 15:9788,
    16:9658, 17:9668, 18:8597, 19:8252, 20:182, 21:167, 22:9644, 23:8616,
    24:8593, 25:8595,26:8594, 27:8592, 28:8735, 29:8596, 30:9650, 31:9660,
    32:32, 33:33, 34:34, 35:35, 36:36, 37:37, 38:38, 39:39,
    40:40, 41:41, 42:42, 43:43, 44:44, 45:45, 46:46, 47:47,
    48:48, 49:49, 50:50, 51:51, 52:52, 53:53, 54:54, 55:55,
    56:56, 57:57, 58:58, 59:59, 60:60, 61:61, 62:62, 63:63,
    64:64, 65:65, 66:66, 67:67, 68:68, 69:69, 70:70, 71:71,
    72:72, 73:73, 74:74, 75:75, 76:76, 77:77, 78:78, 79:79,
    80:80, 81:81, 82:82, 83:83, 84:84, 85:85, 86:86, 87:87,
    88:88, 89:89, 90:90, 91:91, 92:92, 93:93, 94:94, 95:95,
    96:96, 97:97, 98:98, 99:99, 100:100, 101:101, 102:102, 103:103,
    104:104, 105:105, 106:106, 107:107, 108:108, 109:109, 110:110, 111:111,
    112:112, 113:113, 114:114, 115:115, 116:116, 117:117, 118:118, 119:119,
    120:120, 121:121, 122:122, 123:123, 124:124, 125:125, 126:126, 127:8962,
    128:199, 129:252, 130:233, 131:226, 132:228, 133:224, 134:229, 135:231,
    136:234, 137:235, 138:232, 139:239, 140:238, 141:236, 142:196, 143:197,
    144:201, 145:230, 146:198, 147:244, 148:246, 149:242, 150:251, 151:249,
    152:255, 153:214, 154:220, 155:162, 156:163, 157:165, 158:8359, 159:402,
    160:225, 161:237, 162:243, 163:250, 164:241, 165:209, 166:170, 167:186,
    168:191, 169:8976, 170:172, 171:189, 172:188, 173:161, 174:171, 175:187,
    176:9617, 177:9618, 178:9619, 179:9474, 180:9508, 181:9569, 182:9570, 183:9558,
    184:9557, 185:9571, 186:9553, 187:9559, 188:9565, 189:9564, 190:9563, 191:9488,
    192:9492, 193:9524, 194:9516, 195:9500, 196:9472, 197:9532, 198:9566, 199:9567,
    200:9562, 201:9556, 202:9577, 203:9574, 204:9568, 205:9552, 206:9580, 207:9575,
    208:9576, 209:9572, 210:9573, 211:9561, 212:9560, 213:9554, 214:9555, 215:9579,
    216:9578, 217:9496, 218:9484, 219:9608, 220:9604, 221:9612, 222:9616, 223:9600,
    224:945, 225:223, 226:915, 227:960, 228:931, 229:963, 230:181, 231:964,
    232:934, 233:920, 234:937, 235:948, 236:8734, 237:966, 238:949, 239:8745,
    240:8801, 241:177, 242:8805, 243:8804, 244:8992, 245:8993, 246:247, 247:8776,
    248:176, 249:8729, 250:183, 251:8730, 252:8319, 253:178, 254:9632, 255:160,
}

var world = null;
var board_number = null;
var board = null;

var canvas = null;
var ctx = null;
var filename = null;
var CHARSET_IMAGE = null;
var CHARSET_NAME = null;
var CANVAS_WIDTH = 480;
var CANVAS_HEIGHT = 350;
var TILE_WIDTH = 8;
var TILE_HEIGHT = 14;
var renderer = null;
var hover_x = 0;
var hover_y = 0;

function init()
{
    renderer = new Renderer();
    renderer.render = renderer[$("select[name=renderer]").val()];
    $(".zip-content").show();

    if (load_file)
    {
        auto_load();
    }
}

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

var switch_board = function (e)
{
    e.preventDefault();
    var board_number = $(this).attr("data-board");
    $("li.board[data-board-number="+board_number+"]").click();
    return true;
}

function pull_file()
{
    if ($(this).hasClass("selected"))
        return false;

    $("#file-list li").removeClass("selected");
    $("#file-list li ol").remove();
    $("#file-list li br").remove();
    $(this).addClass("selected");
    filename = $(this).contents().filter(function(){ return this.nodeType == 3; })[0].nodeValue;
    var split = filename.toLowerCase().split(".");
    var head = split[0];
    var ext = split[split.length - 1];

    // Fix for files with no extension
    if (filename.indexOf(".") == -1)
        ext = "txt";

    if (filename == "Title Screen")
    {
        $("#details").html(`<img src="${$(this).data("img")}">`);
        return true;
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
            "filename":filename,
            "format":"auto",
            "uploaded":uploaded,
        }
    }).done(function (data){
        var format = "txt";  // Default to text mode

        if (ext == "zzt" || ext == "sav" || ext == "szt")
        {
            format = (ext != "szt") ? "zzt" : "szt";
            ELEMENTS = (format == "szt") ? SZZT_ELEMENTS : ZZT_ELEMENTS;
            ENGINE = engines[format];

            world = parse_world(format, data);

            // Write the board names to the file list
            var board_list = create_board_list();
            $("#file-list li.selected").append(board_list);
            $("li.board").click(render_board); // Bind event

            // Auto Load board
            if (load_board != "")
                auto_load_board(load_board);
            else
                tab_select("help");
        }
        else if (ext == "brd")
        {
            format = "zzt";
            ELEMENTS = (format == "szt") ? SZZT_ELEMENTS : ZZT_ELEMENTS;
            ENGINE = engines[format];
            console.log("BRD PARSE");
            world = new World(data);
            world.brd = true;
            var board = parse_board(world);
            world.boards.push(board);
            render_board();
        }
        else if (ext == "hi" || ext == "mh")
        {
            format = "txt";
            var scores = parse_scores(data);
            var output = `<div class='high-scores'>Score &nbsp;Name<br>\n`;
            output += `----- &nbsp;----------------------------------<br>\n`;
            for (var idx in scores)
            {
                output += scores[idx].score + " &nbsp;" + scores[idx].name + "<br>";
            }
            output += "</div>";
            $("#details").html(output);
        }
        else if (["jpg", "jpeg", "gif", "bmp", "png", "ico"].indexOf(ext) != -1)
        {
            format = "img";
            var zip_image = new Image();
            zip_image.src = data;
            $("#details").html(`<img id='zip_image' alt='Zip file image'>`);
            $("#zip_image").attr("src", `data:image/'${ext}';base64,${data}`);
        }
        else if (["avi"].indexOf(ext) != -1)
        {
            format = "video";
            // TODO: Make this actually work (many many years from now)
            $("#details").html(`<video id='zip_video' alt='Zip file video'></video>`);
            $("#zip_video").attr("src", `data:video/x-msvideo;base64,${data}`);
            // MIME would vary, but there's only one avi file in the DB.
            // Not surprisingly msvideo was not adapted into the HTML5 spec.
        }
        else if (["wav", "mp3", "ogg", "mid", "midi"].indexOf(ext) != -1)
        {
            format = "audio";
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
            source.buffer = audio_buffer; // tell the source which sound to play
            source.connect(context.destination); // connect the source to the context's destination (the speakers)
            source.start(0)

            //$("#details").html("<audio id='zip_audio' src='"+zip_audio_url+"'>Your browser does not support HTML5 audio</audio>");
        }
        else if (ext == "com")
        {
            format = "img";
            // Load the font
            var font_filename = ("0000" +db_id).slice(-4) + "-" + filename.slice(0, -4) + ".png";
            $("select[name=charset]").val(font_filename);

            // Display the font
            $("#details").html(`<img src='/static/images/charsets/${font_filename}' class='charset' alt='${filename}' title='${filename}'>`);
        }
        else // Text mode
        {
            $("#details").html(data);
            $("#filename").text(filename);
        }

        // Update the format for CSS purposes
        $("#details").attr("data-format", format);
        $("#details").scrollTop(0);
    });
}

function load_local_file()
{
    var file = $("#local-file-path").get(0).files[0];
    console.log(file);
    var url = window.URL || window.webkitURL;
    var blob = url.createObjectURL(file);
    console.log(blob)

    var file_reader = new FileReader();
    file_reader.onload = function (e) {
        // Determine engine
        var ext = file["name"].slice(-3).toLowerCase();
        var format = (ext != "szt") ? "zzt" : "szt";
        console.log("FORMAT", format, ext)
        ELEMENTS = (format == "szt") ? SZZT_ELEMENTS : ZZT_ELEMENTS;
        ENGINE = engines[format];

        $("#local-file-name").text(file["name"]);
        $("#local-file-name").addClass("selected");
        var byte_array = new Uint8Array(file_reader.result);
        var hex_string = "";

        for (var idx in byte_array)
        {
            hex_string += ("0" + byte_array[idx].toString(16)).slice(-2);
        }
        world = parse_world(format, hex_string);

        var board_list = create_board_list();
        $("#file-list li.selected").append(board_list);
        $("li.board").click(render_board); // Bind event

        $("#details").attr("data-format", format);
        $("#details").scrollTop(0);
    }

    file_reader.readAsArrayBuffer(file);
}

function parse_world(type, data)
{
    // ZZT World Parsing
    var world = new World(data);
    world.format = type;

    if (world.format == "szt")
    {
        renderer.render = renderer["szzt_standard"];
        /*TILE_WIDTH = 8;
        TILE_HEIGHT = 8;*/
        CANVAS_WIDTH = 8 * 96;
        CANVAS_HEIGHT = 14 * 80;
        $("#details").html(
            `<div id='overlay' class='cp437'></div>
            <canvas id='world-canvas'
            width='${CANVAS_WIDTH}'
            height='${CANVAS_HEIGHT}'
            </canvas>`
        );
        $("select[name=charset]").val("szzt-cp437.png");
    }
    else
    {
        // Default these out
    }

    // Parse World Bytes
    world.world_bytes = world.read(2);

    if (world.world_bytes != engines[type]["identifier"])
    {
        $("#details").html(
            `World is not valid. Got ${world.world_bytes}.
            Expected ${identifier}`
        );
        return false;
    }

    // Parse Number of Boards (this starts at 0 for a title screen only)
    world.board_count = world.read(2);

    // Parse World Stats
    world.ammo = world.read(2)
    world.gems = world.read(2)
    world.keys = [];
    for (var x = 0; x < 7; x++)
        world.keys.push(world.read(1));
    world.health = world.read(2);
    world.starting_board = world.read(2);

    // Begin parsing World information
    if (type == "zzt")
    {
        world.torches = world.read(2);
        world.torch_cycles = world.read(2);
        world.energizer_cycles = world.read(2);
        world.read(2); // Unused bytes
        world.score = world.read(2);
        world.name_length = world.read(1);
        world.name = world.str_read(ENGINE.max_world_length).substr(0,world.name_length);
    }
    else if (type == "szt")
    {
        world.read(2); // Unused
        world.score = world.read(2);
        world.read(2); // Unused
        world.energizer_cycles = world.read(2);
        world.name_length = world.read(1);
        world.name = world.str_read(ENGINE.max_world_length).substr(0,world.name_length);
    }

    // Parse Flags
    for (var x = 0; x < ENGINE.max_flags; x++)
    {
        var len = world.read(1);                              // Read flag length
        world.flags.push(world.str_read(20).substr(0,len));   // Read flag name
    }

    world.time_passed = world.read(2);
    world.read(2)                       // Unused playerdata
    world.save = (world.read(1) != 0);  // Save/Lock file

    if (type == "szt")
    {
        world.z = world.read(2); // z-counter
    }
    // End Parsing World information

    // Parse Boards
    world.idx = ENGINE.first_board_index;
    for (var x = 0; x <= world.board_count; x++)
    {
        world.boards.push(parse_board(world));
    }

    if (world.brd)
        var world_kind = "Board";
    else if (world.save)
        var world_kind = "Save";
    else
        var world_kind = "World";

    var key_display = `<div class='cp437' id='key-list'>`;
    for (var idx in world.keys)
    {
        var color = colors[parseInt(idx) + 9];
        var bg = colors[parseInt(idx) + 1];
        if (world.keys[idx] != 0)
            key_display += `<span style='color:${color};background:${bg};'>♀</span>`;
        else
            key_display += `&nbsp;`;
    }
    key_display += `</div>`;

    var output = `<table class='fv col'>
        <tr><td>Format:</td><td>${type.toUpperCase()} ${world_kind}</td></tr>
        <tr><td>Name:</td><td>${world.name}</td></tr>
        <tr><td>Boards:</td><td>${world.board_count + 1}</td></tr>
        <tr><td>Health:</td><td>${world.health}</td></tr>
        <tr><td>Ammo:</td><td>${world.ammo}</td></tr>
        <tr><td>Torches:</td><td>${world.torches}</td></tr>
        <tr><td>Gems:</td><td>${world.gems}</td></tr>
        <tr><td>Keys:</td><td>${key_display}</td></tr>
        <tr><td>Score:</td><td>${world.score}</td></tr>
        <tr><td>Torch Cycles:</td><td>${world.torch_cycles}</td></tr>
        <tr><td>Energizer Cycles:</td><td>${world.energizer_cycles}</td></tr>
        <tr><td>Time Elapsed:</td><td>${world.time_passed}</td></tr>
    `;
    output += `</table>`;

    output += `<table class='fv col'>`;
    for (var idx in world.flags)
    {
        if (world.flags[idx])
            output += `<tr><td>Flag ${idx}:</td><td>${world.flags[idx]}</td></tr>`;
    }
    output += `</table>`;

    $("#world-info").html(output);
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
    board.title = world.str_read(ENGINE.max_board_length).substr(0,board.title_length);

    // Placeholder way to deal with invalid elements
    if (ELEMENTS.length < 256)
    {
        while (ELEMENTS.length < 256)
            ELEMENTS.push(
                {
                "id":ELEMENTS.length,
                "name":"Unknown Element " + ELEMENTS.length,
                "oop_name":"",
                "character":63
                }
            );
    }

    // Parse Elements
    var parsed_tiles = 0;

    while (parsed_tiles < ENGINE.tile_count)
    {
        var quantity = world.read(1);
        if (quantity == 0)
            quantity = 256;
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
                    "name":ELEMENTS[element_id]["name"],
                    "character":ENGINE.characters[element_id], // This is the default character before any additional board/stat parsing
                    "color_id":color,
                    "foreground":color % 16,
                    "background":parseInt(color / 16),
                    "foreground_name":COLOR_NAMES[color % 16],
                    "background_name":COLOR_NAMES[Math.floor(color / 16)]
                }
            );
        }
        parsed_tiles += quantity;
    }

    // Parse Properties
    if (world.format == "zzt")
    {
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
    }
    else if (world.format == "szt")
    {
        board.max_shots = world.read(1);
        board.exit_north = world.read(1);
        board.exit_south = world.read(1);
        board.exit_west = world.read(1);
        board.exit_east = world.read(1);
        board.zap = world.read(1);
        board.enter_x = world.read(1);
        board.enter_y = world.read(1);
        board.camera_x = world.read(2);
        board.camera_y = world.read(2);
        board.time_limit = world.read(2);
        world.read(14) // Unused
        board.stat_count = world.read(2);
    }

    board.stats = [];
    // End board properties

    // Parse Stats
    var parsed_stats = 0;
    var oop_read = 0;

    while (parsed_stats <= board.stat_count)
    {
        var stat = {};
        stat.idx = parsed_stats;
        stat.x = world.read(1);
        stat.y = world.read(1);
        stat.tile_idx = ((stat.y-1) * ENGINE.board_width) + (stat.x-1);
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

        if (world.format == "zzt")
            world.read(8); // Padding

        if (stat.oop_length > 32767) // Pre-bound element
            stat.oop_length = 0;

        if (stat.oop_length)
        {
            stat.oop = world.str_read(stat.oop_length);
            oop_read += stat.oop_length;

            // Escape HTML
            stat.oop = stat.oop.replace(/</g, "&lt;");
            stat.oop = stat.oop.replace(/>/g, "&gt;");
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
    if ((world.idx != manual_idx) && (world.brd != true))
    {
        board.corrupt = true;
        world.idx = manual_idx;
    }
    return board;
}

function render_board()
{
    board_number = $(this).data("board-number") || 0;
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
        output += `<div class='error'>This board is corrupt</div>`;
        $("#board-info").html(output);
        tab_select("board-info");
        return true;
    }

    output += `<table class='fv col'>
    <tr>
        <td>Title:</td><td>${board.title}</td>
    </tr>
    <tr>
        <td>Can Fire:</td><td>${board.max_shots} shot${((board.max_shots != 1) ? "s" : "")}</td>
        <td>Board Is Dark:</td><td>${(board.dark ? "Yes" : "No")}</td>
    </tr>

    <tr><td>Re-enter When Zapped:</td><td>${(board.zap ? "Yes" : "No")}</td>
        <td>Re-enter X/Y:</td><td>${board.enter_x} / ${board.enter_y}</td>
    </tr>
    <tr><td>Time Limit:</td>
        <td>${board.time_limit ? "None": board.time_limit + " sec"+(board.time_limit != 1 ? "s" : "")}.</td>
        <td>&nbsp;</td><td>&nbsp;</td>
    </tr>
    <tr>
        <td>Stat Elements:</td><td>${board.stat_count + 1} / 151</td>
        <td>Board Size:</td><td>${board.size + 2} bytes</td>
    </tr>`;

    if (board.message != "")
        output += `<tr><td>Message:</td><td>${board.message}</td></tr>`;

    output += `<tr>
        <th colspan="4">Board Exits</th>
    </tr>`

    var arrows = ["↑", "→", "←", "↓"]
    var props= ["exit_north", "exit_east", "exit_west", "exit_south"];
    for (var idx in arrows)
    {
        if (idx % 2 == 0)
            output += `<tr>`;
        output += `<td class='exit'>${arrows[idx]}</td>`;
        if (board[props[idx]] != 0)
            output += `<td><a class="board-link" data-board="${board[props[idx]]}" href="?file=${loaded_file}&board=${board[props[idx]]}">${board[props[idx]]}. ${world.boards[board[props[idx]]].title}</a></td>`;
        else
            output += `<td>None</td>`;
        if (idx % 2 != 0)
            output += `</tr>`;
    }

    output += `</table>`;

    $("#board-info").html(output);
    tab_select("board-info");

    // Bind board links
    $(".board-link").click(switch_board);

    // Render the stat info as well
    render_stat_list();
    return true;
}

function draw_board()
{
    ctx.globalCompositeOperation = "source-over";
    ctx.fillstyle = "black";
    ctx.fillRect(0,0,CANVAS_WIDTH,CANVAS_HEIGHT);
    var board_number = $(".board.selected").data("board-number") || 0;
    if (board_number == null)
        return false;

    console.log("DRAWING A BOARD", board_number);
    var board = world.boards[board_number];

    renderer.render(board);
    console.log("Rendered.");
    $("#world-canvas").click(stat_info);
    $("#world-canvas").dblclick({"board": board}, passage_travel);

    // Click coordinates in hash
    if (hash_coords)
    {
        console.log("Auto clicking element...", hash_coords);
        var sliced = hash_coords.slice(1);
        var split = sliced.split(",");
        var e = {"data":{"x":split[0], "y":split[1]}};
        stat_info(e);
    }
}

var passage_travel = function(e) {
    var posX = $(this).offset().left;
    var posY = $(this).offset().top;
    var x = parseInt((e.pageX - posX) / TILE_WIDTH) + 1;
    var y = parseInt((e.pageY - posY) / TILE_HEIGHT) + 1;
    var tile_idx = ((y-1) * 60) + (x-1);
    var board = world.boards[board_number];

    var destination = null;

    if (board.elements[tile_idx].name == "Passage")
    {
        destination = 0;
        for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
        {
            if (board.stats[stat_idx].x == x && board.stats[stat_idx].y == y)
            {
                destination = board.stats[stat_idx].param3;
            }
        }
    }

    if (destination != null)
        $("li.board[data-board-number="+destination+"]").click();

    return true;
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
    var tile_idx = ((y-1) * ENGINE.board_width) + (x-1);
    var hash_coords = "#" + x + "," + y;

    // Check for out of bounds coordinates
    if (tile_idx < 0 || tile_idx >= ENGINE.tile_count)
        return false;

    //window.location.hash = ;
    history.replaceState(undefined, undefined, hash_coords)

    // Get the current tile
    var tile = world.boards[board_number].elements[tile_idx];

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

    var output = `<table class="fv">
    <tr>
        <td>Position:</td>
        <td>(${x}, ${y}) [${tile_idx}/${ENGINE.tile_count}]</td>
        <td>Def. Character:</td>
        <td>${tile.character}</td>
    </tr>
    <tr>
        <td>Name:</td>
        <td>${tile.name}</td>`

    if (stat != null)
        output += `<td>Cycle:</td><td>${stat.cycle}</td>`;
    else
        output += `<td>&nbsp;</td><td>&nbsp;</td>`;

    output += `</tr>
    <tr>
        <td>ID:</td>
        <td>${tile.id}</td>
        <td>Color:</td>
        <td>${tile.foreground_name} on ${tile.background_name} (${tile.color_id})</td>
    </tr>
    `;

    if (stat != null)
    {
        var p1name = (ELEMENTS[tile.id].hasOwnProperty("param1") ? ELEMENTS[tile.id].param1 : "Param1");
        var p2name = (ELEMENTS[tile.id].hasOwnProperty("param2") ? ELEMENTS[tile.id].param2 : "Param2");
        var p3name = (ELEMENTS[tile.id].hasOwnProperty("param3") ? ELEMENTS[tile.id].param3 : "Param3");
        var param3_display = stat.param3;

        if (tile.name == "Passage")
        {
            var loaded_file = $("#file-list ul > li.selected").contents().filter(function(){ return this.nodeType == 3; })[0].nodeValue;
            param3_display = `<a class="board-link" data-board="${stat.param3}" href="?file=${loaded_file}&board=${stat.param3}">${stat.param3} - ${world.boards[stat.param3].title}</a>`;
        }

        output += `
        <tr>
            <td>Under ID:</td><td>${ELEMENTS[stat.under_id].name}</td>
            <td>Under Color:</td><td>${ELEMENTS[stat.under_id].name}</td>

        </tr>
        <tr>
            <td>${p1name}:</td><td>${stat.param1}</td>
            <td>X/Y-Step:</td><td>(${stat.x_step}, ${stat.y_step})</td>
        </tr>
        <tr>
            <td>${p2name}:</td><td>${stat.param2}</td>
            <td>Leader:</td><td>${stat.leader}</td>
        </tr>
        <tr>
            <td>${p3name}:</td><td>${param3_display}</td>
            <td>Follower:</td><td>${stat.follower}</td>
        </tr>
        <tr>
            <td>OOP Length:</td><td>${stat.oop_length}</td>
            <td>Instruction:</td><td>${stat.oop_idx}</td>
        </tr>
        </table>
        `;

        if (stat.oop_length > 0)
        {
            output += `<code class='zzt-oop'>${syntax_highlight(stat.oop)}</code>`;
        }
    }

    $("#element-info").html(output);
    tab_select("element-info");
    // Bind board links (from passages)
    $(".board-link").click(switch_board);

    return true;
}

function tab_select(selector)
{
    $("#file-data > div").hide();
    $("#file-tabs li").removeClass("selected");
    $("li[name="+selector+"]").addClass("selected");
    $("#"+selector).show();
}

$(window).bind("load", function() {
    $("#local-load").click(load_local_file);

    $("#file-list li").click({"format": "auto"}, pull_file);
    $("#file-tabs ul li").click(function (){tab_select($(this).attr("name"))});

    // Stat sorting
    $("select[name=stat-sort]").change(render_stat_list);

    $("select[name=charset]").change(load_charset);
    $("input[name=2x]").change(load_charset);

    // Renderer
    $("select[name=renderer]").change(function (){
        renderer.render = renderer[$(this).val()];
        $("li.selected.board").click();
        $("li[name=preferences]").click();
    });

    // Invisibles, Monitors, and Board Edges
    $("select[name=invisibles]").change(function (){
        renderer.invisible_style = $(this).val();
        renderer.render(world.boards[board_number]);
    });
    $("select[name=monitors]").change(function (){
        renderer.monitor_style = $(this).val();
        renderer.render(world.boards[board_number]);
    });
    $("select[name=edges]").change(function (){
        renderer.edge_style = $(this).val();
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
            $("li.board.selected").next().click();
        else if (e.keyCode == 109 || e.keyCode == 173 || e.keyCode == 75) // Previous Board
            $("li.board.selected").prev().click();
        else if (e.keyCode == 87) // World
            $("li[name=world-info]").click();
        else if (e.keyCode == 66) // Board
            $("li[name=board-info]").click();
        else if (e.keyCode == 69) // Element
            $("li[name=element-info]").click();
        else if (e.keyCode == 83) // Stat
            $("li[name=stat-info]").click();
        else if (e.keyCode == 80) // Prefs.
            $("li[name=preferences]").click();
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

    // Activate the file viewer
    init();
    //var timeout = window.setTimeout(init, 5000);

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
        if (world && world.format == "szt")
        {
            selected_charset = "szzt-cp437.png";
        }

        console.log("I'm hitting load charset?", selected_charset);
        CHARSET_NAME = selected_charset;
        CHARSET_IMAGE = new Image();
        CHARSET_IMAGE.src = "/static/images/charsets/"+CHARSET_NAME;
        CHARSET_IMAGE.addEventListener("load", function ()
        {
            CANVAS_WIDTH = CHARSET_IMAGE.width / 16 * ENGINE.board_width;
            CANVAS_HEIGHT = CHARSET_IMAGE.height / 16 * ENGINE.board_height;

            TILE_WIDTH = CANVAS_WIDTH / ENGINE.board_width;
            TILE_HEIGHT = CANVAS_HEIGHT / ENGINE.board_height;

            $("#details").html(`
                <div id='overlay'></div><canvas id='world-canvas' width='${CANVAS_WIDTH}' height='${CANVAS_HEIGHT}'>Your browser is outdated and does not support the canvas element.</canvas>
            `);
            canvas = document.getElementById("world-canvas");
            ctx = canvas.getContext("2d");

            init_overlay();
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
                oop[idx] = `<span class='name'>@</span><span class='yellow'>${oop[idx].slice(1)}</span>`;
            else if (oop[idx][0] && oop[idx][0] == "#")
            {
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
            else if (oop[idx][0] && oop[idx][0] == "!")
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
        }
        return oop.join("\n");
}

function render_stat_list()
{
    console.log("RENDERING STATS")
    var board = world.boards[board_number];
    var stat_list = "";

    // Sort method
    var sort = $("select[name=stat-sort]").val();
    if (sort == "stat")
    {
        board.stats.sort(function(a, b){
            return a.idx - b.idx;
        });
    }
    else if (sort == "coord")
    {
        board.stats.sort(function(a, b){
            return a.tile_idx - b.tile_idx;
        });
    }
    else if (sort == "name")
    {
        board.stats.sort(function(a, b){
            var stat_name1 = world.boards[board_number].elements[a.tile_idx].name;
            if ((stat_name1 == "Scroll" || stat_name1 == "Object") && a.oop[0] == "@")
                stat_name1 = a.oop.slice(0, a.oop.indexOf("\r"));

            var stat_name2 = world.boards[board_number].elements[b.tile_idx].name;
            if ((stat_name2 == "Scroll" || stat_name2 == "Object") && b.oop[0] == "@")
                stat_name2 = b.oop.slice(0, b.oop.indexOf("\r"));

            if (stat_name1.toLowerCase() < stat_name2.toLowerCase())
                return -1;
            else if (stat_name1.toLowerCase() > stat_name2.toLowerCase())
                return 1;
            else
                return 0;
        });
    }
    else if (sort == "code")
    {
        board.stats.sort(function(a, b){
            if (a.oop_length < b.oop_length)
                return 1;
            else if (a.oop_length > b.oop_length)
                return -1;
            else
                return 0;
        });
    }

    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
    {
        var stat = board.stats[stat_idx];

        // Invalid stat check
        if ((stat.tile_idx < 0) || (stat.tile_idx >= ENGINE.tile_count))
        {
            console.log("Invalid stat detected!")
            if (stat.oop.length == 0)
                stat_list += `<li class='empty'>`;
            else
                stat_list += `<li>`;
            stat_list += `
                <a class='jsLink' name='stat-link' data-x='${stat.x}' data-y='${stat.y}'>
                (${("00"+stat.x).slice(-2)}, ${("00"+stat.y).slice(-2)}) [????] UNKNOWN</a> `
            if (stat.oop.length)
                stat_list += `${stat.oop.length} bytes`;
            stat_list += `</li>\n`;
            continue;
        }
        var stat_name = board.elements[stat.tile_idx].name;
        if ((stat_name == "Scroll" || stat_name == "Object") && stat.oop[0] == "@")
            stat_name = stat.oop.slice(0, stat.oop.indexOf("\r"));

        if (stat.oop.length == 0)
            stat_list += `<li class='empty'>`;
        else
            stat_list += `<li>`;
        stat_list += `
            <a class='jsLink' name='stat-link' data-x='${stat.x}' data-y='${stat.y}'>
            (${("00"+stat.x).slice(-2)}, ${("00"+stat.y).slice(-2)}) [${(("0000"+(stat.tile_idx+1)).slice(-4))}]
            ${stat_name}</a> `;
        if (stat.oop.length)
                stat_list += `${stat.oop.length} bytes`;
            stat_list += `</li>\n`;
    }
    $("#stat-info ol").html(stat_list);
    $("a[name=stat-link]").click(function (){
        var e = {"data":{"x":$(this).data("x"), "y":$(this).data("y")}};
        stat_info(e);
    });

    $("a[name=stat-link]").hover(function (){
        highlight($(this).data("x"), $(this).data("y"));
    }, function (){
        unhighlight($(this).data("x"), $(this).data("y"));
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

function init_overlay()
{
    $("#overlay").hide();
    $("#overlay").html(`(<span id='overlay-x'>00</span>, <span id='overlay-y'>00</span>) [<span id='overlay-tile'>0000</span>]<br><div class='color-swatch'></div> <span id='overlay-element'></span>`);

    $("#world-canvas").mousemove(update_overlay);
    $("#world-canvas").mouseout(hide_overlay);
}

function update_overlay(e)
{
    $("#overlay").show();
    var posX = $(this).offset().left;
    var posY = $(this).offset().top;
    var x = parseInt((e.pageX - posX) / TILE_WIDTH) + 1;
    var y = parseInt((e.pageY - posY) / TILE_HEIGHT) + 1;
    var tile_idx = ((y-1) * ENGINE.board_width) + (x-1);

    if (x != hover_x || y != hover_y)
    {
        hover_x = x;
        hover_y = y;

        $("#overlay-x").text(("00"+x).slice(-2));
        $("#overlay-y").text(("00"+y).slice(-2));
        $("#overlay-tile").text(("0000"+(tile_idx+1)).slice(-4));

        // Element
        var element = world.boards[board_number].elements[tile_idx];
        $("#overlay-element").text(element.name);

        // Color
        var bg_x = parseInt((element.foreground) * -8); // TODO: Tile W/H for SZZT
        var bg_y = parseInt((element.background) * -14);
        $("#overlay .color-swatch").css("background-position", bg_x+"px "+ bg_y + "px");
    }

    return true;
}

function hide_overlay(e)
{
    $("#overlay").hide();
}

function highlight(x, y)
{
    print(ctx, 201, 127, x - 2, y - 2);
    print(ctx, 205, 127, x - 1, y - 2);
    print(ctx, 187, 127, x, y - 2);
    print(ctx, 186, 127, x - 2, y - 1);
    print(ctx, 186, 127, x, y - 1);
    print(ctx, 200, 127, x - 2, y);
    print(ctx, 205, 127, x - 1, y);
    print(ctx, 188, 127, x, y);
}

function unhighlight(x, y)
{
    var temp_hash_coords = hash_coords;
    hash_coords = null;
    draw_board();
    hash_coords = temp_hash_coords;
}

function create_board_list()
{
    var board_list = `<ol start='0'>`;
    for (var x = 0; x < world.boards.length; x++)
    {
        board_list += `<li class='board${world.starting_board == x ? " b" : ""}' data-board-number='${x}'>`;

        var formatted_num = (x >= 10 ? x : `&nbsp;` + x);
        var formatted_title = world.boards[x].title ? world.boards[x].title : `-untitled`;
        board_list += `
            <div name='board_idx'>${formatted_num}.</div>
            <div name='board_name'>${formatted_title}
            </div>
        `;

        if (world.starting_board == x)
            board_list += `</b>`;
        board_list += `</li>\n`;
    }
    board_list += `</ol><br>\n`;
    return board_list;
}
