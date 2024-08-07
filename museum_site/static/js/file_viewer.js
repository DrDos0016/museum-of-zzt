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
var DETAIL_SZZT_BOARD = 23;

var engines = {
    "zzt":{
        "name": "ZZT",
        "identifier": 0xFFFF,
        "max_world_length": 20,
        "max_flags": 10,
        "tile_count": 1500,
        "max_board_length": 50,
        "first_board_index": 1024,
        "board_width": 60,
        "board_height": 25,
        "character_width": 8,
        "character_height": 14,
        "elements": ["Empty", "Board Edge", "Messenger", "Monitor", "Player", "Ammo", "Torch", "Gem", "Key", "Door", "Scroll", "Passage", "Duplicator", "Bomb", "Energizer", "Star", "Conveyor, Clockwise", "Conveyor, Counterclockwise", "Bullet", "Water", "Forest", "Solid Wall", "Normal Wall", "Breakable Wall", "Boulder", "Slider, North-South", "Slider, East-West", "Fake Wall", "Invisible Wall", "Blink Wall", "Transporter", "Line Wall", "Ricochet", "Blink Ray, Horizontal", "Bear", "Ruffian", "Object", "Slime", "Shark", "Spinning Gun", "Pusher", "Lion", "Tiger", "Blink Ray, Vertical", "Centipede Head", "Centipede Segment", "Text, Blue", "Text, Green", "Text, Cyan", "Text, Red", "Text, Purple", "Text, Yellow", "Text, White"],
        "characters": [32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 179, 92, 248, 176, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 62, 249, 42, 205, 153, 5, 2, 42, 94, 24, 16, 234, 227, 186, 233, 79, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63]
        },
    "szt":{
        "name": "Super ZZT",
        "identifier": 0xFFFE,
        "max_world_length": 20,
        "max_flags": 16,
        "tile_count": 7680,
        "max_board_length": 60,
        "first_board_index": 2048,
        "board_width": 96,
        "board_height": 80,
        "character_width": 16,
        "character_height": 14,
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
};

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
var SCALE = 1;
var renderer = null;
var oop_style = "modern";
var raw_doc = "";

var KEY = {
    "NP_PLUS": 107, "NP_MINUS": 109,
    "NP_UP": 104, "NP_DOWN": 98, "NP_RIGHT": 102, "NP_LEFT": 100,
    "PLUS": 61, "MINUS": 173,
    "B": 66, "E": 69, "J": 74, "K": 75, "P": 80, "S": 83, "W": 87,
};

var overlay = {
    corner: "TL",
    hover_x: 0,
    hover_y: 0,
    html_template: `<div id="overlay">
        (<span id='overlay-x'>00</span>, <span id='overlay-y'>00</span>)
        [<span id='overlay-tile'>0000</span>]<br>
        <div class='color-swatch'></div> <span id='overlay-element'></span>
    </div>`,

    update: function(e) {
        if ($("#fv-left-sidebar").css("visibility") != "visible")
            $("#fv-left-sidebar").css("visibility", "visible");

        var rect = canvas.getBoundingClientRect();
        var raw_x = e.pageX - rect.left - document.querySelector("html").scrollLeft;
        var raw_y = e.pageY - rect.top - document.querySelector("html").scrollTop;

        // Calculate ZZT tile
        var x = parseInt(raw_x / (TILE_WIDTH * SCALE)) + 1;
        var y = parseInt(raw_y / (TILE_HEIGHT * SCALE)) + 1;
        var tile_idx = ((y-1) * ENGINE.board_width) + (x-1);

        if (x != this.hover_x || y != this.hover_y)
        {
            this.hover_x = x;
            this.hover_y = y;
        }
        else
        {
            return false;
        }

        $("#overlay-x").text(("00"+x).slice(-2));
        $("#overlay-y").text(("00"+y).slice(-2));
        $("#overlay-tile").text(("0000"+(tile_idx+1)).slice(-4));

        // Element
        var element = world.boards[board_number].elements[tile_idx];
        $("#overlay-element").text(element.name);

        // Color
        var bg_x = parseInt((element.foreground) * -8);
        var bg_y = parseInt((element.background) * -14);
        $("#fv-left-sidebar .color-swatch").css("background-position", bg_x+"px "+ bg_y + "px");

        // Position
        //console.log("Current POS", this.corner, raw_y, raw_x);
        if (this.corner == "TL" && raw_y < 80 && raw_x <= 180)
        {
            var margin = Math.min(720, $("#world-canvas").height()) - $("#overlay").outerHeight();
            this.corner = "BL";
            $("#overlay").css("margin-top", margin + "px");
        }
        else if (this.corner == "BL" && raw_y >= 270 && raw_x <= 180)
        {
            $("#overlay").css("margin-top", "0px");
            this.corner = "TL";
        }
        return true;
    },

    hide: function() {
        if ($("#fv-left-sidebar").css("visibility") != "hidden")
            $("#fv-left-sidebar").css("visibility", "hidden");
        return true;
    }

};

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
    this.unterminated_flags = [];       // List of unterminated flags
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
        output = parseInt(output, 16);
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

    this.lock_check = function ()
    {
        this.locks = [];

        // Regular Lock
        for (var idx in this.flags)
        {
            if (this.flags[idx].toUpperCase() == "SECRET")
                this.locks.push("Regular Lock");
        }

        // Super Lock
        var last_idx = this.boards.length - 1;
        if (this.boards[last_idx].title == ":c" && this.boards[last_idx].corrupt)
            this.locks.push("Super Lock");

        // Save Lock
        if (this.save)
            this.locks.push("Save Lock");

        if (this.locks.length == 0)
            this.locks = ["None"];
    };

    this.locks_as_string = function ()
    {
        var output = "";
        for (var idx in this.locks)
        {
            output += this.locks[idx] + ", ";
        }
        return output.slice(0, -2);
    };
};

var switch_board = function (e)
{
    e.preventDefault();
    var board_number = $(this).attr("data-board");
    $("li.board[data-board-number="+board_number+"]").click();
    return true;
};

function pull_file()
{
    $("#fv-prefix").remove();
    if ($(this).hasClass("selected"))
    {
        console.log("CLOSING");
        console.log("Zip-content?", $(this).hasClass("zip-content"));
        close_file($(this));
        return false;
    }

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

    console.log("Pull File:", $(this).html());
    if ($(this).hasClass("preview-image-link"))
    {
        set_active_envelope("preview");
        return true;
    }

    // Add to history
    var state = {"load_file": encodeURIComponent(filename), "load_board":"", "tab":""};
    var qs = "?file=" + encodeURIComponent(filename) + window.location.hash;
    if (! history.state || (history.state.load_file != encodeURIComponent(filename)))
    {
        history.pushState(state, "", qs);
    }

    // COM files can avoid calling the actual ZIP
    if (ext == "com" || ext == "chr")
    {
        // TODO this is really hacky for Super ZZT fonts even if it works
        var format = "img";
        var font_filename = ("0000" +db_id).slice(-4) + "-" + filename.slice(0, -4) + ".png";
        var font_to_load = "";

        // Check if the font is on the list of dumped fonts
        var font_exists = false;
        $("select[name=charset]").find("option").each(function (){
            console.log($(this).val() + " / " + font_filename);
            if ($(this).val() == font_filename || $(this).val() == ("szzt-" + font_filename))
            {
                font_exists = true;
                font_to_load = $(this).val();
            }
        });

        // Load the font
        if (font_exists)
        {
            $("select[name=charset]").val(font_to_load);

            // Display the font
            $("#fv-image").attr("src", `/static/images/charsets/${font_to_load}`);
            $("#fv-image").css("background", "#000");

            set_active_envelope("image");
        }
        else
        {
            var output = `The specified ${ext} file is either not a custom font or has not yet been converted to PNG for Museum use.`;
            $("#text-body").html(output);
            set_active_envelope("text");
        }
        return true;
    }

    $.ajax({
        url:"/ajax/get_zip_file/",
        data:{
            "letter":letter,
            "zip":zip,
            "filename":filename,
            "format":"auto",
            "uploaded":uploaded,
        }
    }).done(function (data){
        var format = "txt";  // Default to text mode

        if (ext == "zzt" || ext == "sav" || ext == "szt" || ext == "mwz" || ext == "z_t")
        {
            if (ext == "sav")
            {
                format = identify_save_type(data);
            }
            else
                format = (ext != "szt") ? "zzt" : "szt";

            ELEMENTS = (format == "szt") ? SZZT_ELEMENTS : ZZT_ELEMENTS;
            if (engines.hasOwnProperty(format))
                ENGINE = engines[format];
            else
            {
                set_active_envelope("text");
                $("#text-body").html(`Data error: Engine format "${format}" not found.`);
                return false;
            }

            // Adjust the canvas size based on engine
            var canvas_w = ENGINE.character_width * ENGINE.board_width;
            var canvas_h = ENGINE.character_height * ENGINE.board_height;
            $("#world-canvas").attr({"width": canvas_w + "px", "height": canvas_h + "px"});

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
            if (details.indexOf(DETAIL_SZZT_BOARD) != -1)
            {
                format = "szt";
                renderer.render = renderer.szzt_standard;
                CANVAS_WIDTH = 1536;
                CANVAS_HEIGHT = 1120;
                ELEMENTS = SZZT_ELEMENTS;
                ENGINE = engines[format];
                world = new World(data);
            }
            else
            {

                format = "zzt";
                ELEMENTS = ZZT_ELEMENTS;
                ENGINE = engines[format];
                world = new World(data);
            }

            // Adjust the canvas size based on engine
            var canvas_w = ENGINE.character_width * ENGINE.board_width;
            var canvas_h = ENGINE.character_height * ENGINE.board_height;
            $("#world-canvas").attr({"width": canvas_w + "px", "height": canvas_h + "px"});

            world.brd = true;
            world.format = format;
            var board = parse_board(world);
            world.boards.push(board);
            render_board();
        }
        else if (ext == "hi" || ext == "mh" || ext == "hgs")
        {
            console.log("High score file");
            format = "txt";
            if (ext != "hgs")
                var scores = parse_scores(data);
            else
                var scores = parse_szzt_scores(data);
            var output = `<pre class="cp437 high-scores">Score  Name\n`;
            output += `-----  ----------------------------------\n`;
            for (var idx in scores)
            {
                if (scores[idx].score <= 32767)
                    output += `${scores[idx].spaced_score}  ${scores[idx].name}\n`;
            }
            output += "</pre>";

            set_active_envelope("text");
            $("#text-body").html(output);
            $("#text-body").attr("data-ext", ext);
        }
        else if (["jpg", "jpeg", "gif", "bmp", "png", "ico"].indexOf(ext) != -1)
        {
            format = "img";
            var zip_image = new Image();
            zip_image.src = data;
            set_active_envelope("image");
            $("#fv-image").attr("src", `data:image/'${ext}';base64,${data}`);
        }
        else if (["avi"].indexOf(ext) != -1)
        {
            format = "video";
            // TODO: Make this actually work (many many years from now)
            //$("#details").html(`<video id='zip_video' alt='Zip file video'></video>`);
            //$("#zip_video").attr("src", `data:video/x-msvideo;base64,${data}`);
            // MIME would vary, but there's only one avi file in the DB.
            // Not surprisingly msvideo was not adapted into the HTML5 spec.
        }
        else if (["wav", "mp3", "ogg", "mid", "midi"].indexOf(ext) != -1)
        {
            format = "audio";
            // TODO: Make this actually work
            /*
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
            */
            set_active_envelope("audio");
        }
        else if (ext == "com")
        {

        }
        else if (ext == "doc")
        {
            console.log("Loaded a DOC");
            format = "txt";
            var encoding = "auto";

            var doc_header = `<div id="doc-header">
            DOC files are not intended for display in a browser. They may contain visual errors.
            </div>`;

            $("#text-body").html(doc_header + data);
            $("#filename").text(filename);
            set_active_envelope("text");
        }
        else // Text mode
        {
            $("#text-body").html(data);
            $("#filename").text(filename);
            set_active_envelope("text");
        }
    }).fail(function (data){
        $("#text-body").html(data.responseText);
        $("#filename").text(filename);
        set_active_envelope("text");
    });
}

function load_local_file()
{
    var file = $("#local-file-path").get(0).files[0];
    console.log(file);
    var url = window.URL || window.webkitURL;
    var blob = url.createObjectURL(file);
    console.log(blob);

    var file_reader = new FileReader();
    file_reader.onload = function (e) {
        // Determine engine
        var ext = file.name.slice(-3).toLowerCase();

        if (ext == "sav")
        {
            //identify_save_type(data);
            var format = "zzt";
        }


        var format = (ext != "szt") ? "zzt" : "szt";
        ELEMENTS = (format == "szt") ? SZZT_ELEMENTS : ZZT_ELEMENTS;
        ENGINE = engines[format];

        $("#local-file-name").text(file.name);
        $("#local-file-name").addClass("selected");
        var byte_array = new Uint8Array(file_reader.result);
        var hex_string = "";

        for (var idx in byte_array)
        {
            hex_string += ("0" + byte_array[idx].toString(16)).slice(-2);
        }

        // Create world info for BRD files
        if (ext == "brd")
        {
            hex_string = "ffff000000000000000000000000006400000000000000000000000000084155544f47454e57" + "0".repeat(948) + hex_string;
        }

        console.log(hex_string);
        world = parse_world(format, hex_string);

        var board_list = create_board_list();
        $("#file-list li.selected").append(board_list);
        $("li.board").click(render_board); // Bind event
    };

    file_reader.readAsArrayBuffer(file);
}

function parse_world(type, data)
{
    // ZZT World Parsing
    var world = new World(data);
    world.format = type;

    if (world.format == "szt")
    {
        renderer.render = renderer.szzt_standard;
        CANVAS_WIDTH = 1536;
        CANVAS_HEIGHT = 1120;
        if (custom_charset)
            $("select[name=charset]").val(custom_charset);
        else
            $("select[name=charset]").val("szzt-cp437.png");
    }
    else
    {
        // Default these out
        $("select[name=renderer]").val("zzt_standard");
        renderer.render = renderer.zzt_standard;
        CANVAS_WIDTH = 480;
        CANVAS_HEIGHT = 350;
        if (custom_charset)
            $("select[name=charset]").val(custom_charset);
        else
            $("select[name=charset]").val("cp437.png");
    }

    // Parse World Bytes
    world.world_bytes = world.read(2);

    if (world.world_bytes != engines[type].identifier)
    {
        let bad_identifier = world.world_bytes.toString(16);
        bad_identifier = bad_identifier.slice(2,4) + bad_identifier.slice(0,2);

        set_active_envelope("text");
        $("#text-body").html(`File is not valid. Got unsupported identifier of "${bad_identifier}".`);
        $("#text-body").attr("data-ext", "err");
        return false;
    }

    // Parse Number of Boards (this starts at 0 for a title screen only)
    world.board_count = world.read(2);

    // Parse World Stats
    world.ammo = world.read(2);
    world.gems = world.read(2);
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
        world.unterminated_name = world.str_read(ENGINE.max_world_length);
        world.name = world.unterminated_name.substr(0,world.name_length);

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
        var len = world.read(1); // Read flag length
        world.unterminated_flags.push(world.str_read(20)); // Read flag name
        world.flags.push(world.unterminated_flags[x].substr(0,len));
    }

    world.time_passed = world.read(2);
    world.read(2)                       // Unused playerdata
    world.save = (world.read(1) != 0);  // Save/Lock file

    if (type == "szt")
    {
        world.z = world.read(2); // z-counter
    }

    world.unused = world.str_read(14);
    world.watermark = world.str_read((ENGINE.first_board_index - world.idx) / 2);
    // End Parsing (basic) World information

    // Parse Boards
    world.idx = ENGINE.first_board_index;
    for (var x = 0; x <= world.board_count; x++)
    {
        world.boards.push(parse_board(world));
    }

    world.lock_check(); // Boards needs to be parsed to check for Super Locks

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

    var output = `<table class='fv col' name='world-table'>
        <tr><td>Format:</td><td>${type.toUpperCase()} ${world_kind}</td></tr>
        <tr><td>Name:</td><td>${world.name}</td></tr>
        <tr class='fv-hidden-row'><td>Unterminated Name:</td><td>${world.unterminated_name}</td></tr>
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
        <tr><td>Save:</td><td>${(world.save ? "Yes" : "No")}</td></tr>
    `;

    if (world.locks)
        output += `<tr><td>Lock:</td><td>${world.locks_as_string()}</td></tr>`;

    if (world.watermark.replace(/\u0000/g, ""))
        output += `<tr><td>Watermark:</td><td>${world.watermark}</td></tr>`;

    output += `</table>`;

    output += `<table class='fv' name='flag-table'>`;
    for (var idx in world.flags)
    {
        if (world.flags[idx])
            output += `<tr><td>Flag ${idx}:</td><td>${world.flags[idx]}</td></tr>`;
    }
    output += `</table>`;

    output += `<table class='fv' name='search-table' id="search-table">
        <tr><td>ZZT-OOP Search:</td><td><input name="code-search"></td><td><input id="code-search-submit" type="button" value="Search"></td><td><input id="code-search-reset" type="button" value="Reset"></td></tr>
    </table>`;

    output += `<a class="jsLink" id="show-unterminated">Show unterminated values</a>`;

    output += `<table class='fv fv-hidden' name='unterminated-flag-table'>`;
    for (var idx in world.unterminated_flags)
    {
        output += `<tr><td>Flag ${idx}:</td><td>${world.unterminated_flags[idx]}</td></tr>`;
    }
    output += `</table>`;

    $("#world-info").html(output);
    bind_world_widgets();
    return world;
}

function parse_board(world)
{
    var board = {};
    var start_idx = world.idx;

    if (isNaN(start_idx))
    {
        board.title = "Extremely Corrupt Board";
        board.elements = [];
        board.stats = [];
        board.corrupt = true;
        return board;
    }

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


    // Actually parse the tiles
    while (parsed_tiles < ENGINE.tile_count)
    {
        var quantity = world.read(1);
        if (quantity == 0)
            quantity = 256;
        var element_id = world.read(1);

        if (isNaN(element_id))
        {
            console.log("NaN Element!");
            board.corrupt = true;
            break;
        }

        var color = world.read(1);
        procced_bytes += 3;
        board.room.push([quantity, element_id, color]);

        var element = {
            "id":element_id,
            "tile":tile_idx,
            "name":ELEMENTS[element_id]["name"],
            "character":ENGINE.characters[element_id], // This is the default character before any additional board/stat parsing
            "color_id":color,
            "foreground":color % 16,
            "background":parseInt(color / 16),
        }

        for (var tile_idx = 0; tile_idx < quantity; tile_idx++)
        {
            board.elements.push(element);
        }
        parsed_tiles += quantity;
    }

    if (! board.corrupt)
    {
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
            stat.x_step = signed(world.read(2));
            stat.y_step = signed(world.read(2));
            stat.cycle = signed(world.read(2));
            stat.param1 = world.read(1);
            stat.param2 = world.read(1);
            stat.param3 = world.read(1);
            stat.follower = signed(world.read(2));
            stat.leader = signed(world.read(2));
            stat.under_id = world.read(1);
            stat.under_color = world.read(1);
            stat.pointer = world.read(4);
            stat.oop_idx = signed(world.read(2));
            stat.oop_length = signed(world.read(2));
            stat.direction = step_direction(stat.x_step, stat.y_step);

            if (world.format == "zzt")
                world.read(8); // Padding

            if (stat.oop_length > 0)
            {
                stat.oop = world.str_read(stat.oop_length);
                oop_read += stat.oop_length;

                // Escape HTML
                stat.oop = stat.oop.replace(/</g, "&lt;");
                stat.oop = stat.oop.replace(/>/g, "&gt;");
            }
            else if (stat.oop_length == 0)
            {
                stat.oop = "";
            }
            else
            {
                stat.oop = ""; // Pre-bound
            }

            board.stats.push(stat);
            parsed_stats++;
        }
    }

    // Jump to the start of the next board in file (for corrupt boards)
    var manual_idx = (start_idx + board.size * 2) + 4;
    if ((world.idx != manual_idx) && (world.brd != true))
    {
        console.log("Corrupt last case", world.idx, manual_idx);
        board.corrupt = true;
        world.idx = manual_idx;
    }
    return board;
}

function render_board(e)
{
    if (e)
        e.stopPropagation();

    board_number = $(this).data("board-number") || 0; // idk why this breaks if var is gone
    var coordinates = $(this).data("coords") || 0;
    $("li.board").removeClass("selected");
    $(this).addClass("selected");
    load_charset();
    update_scale();

    // Add to history
    var state = {"load_file": filename, "load_board":board_number, "tab":""};
    var qs = "?file=" + encodeURIComponent(filename) + "&board=" + board_number;
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
        <td>Title:</td><td colspan="3"><pre>${board.title}</pre></td>
    </tr>
    <tr>
        <td>Can Fire:</td><td>${board.max_shots} shot${((board.max_shots != 1) ? "s" : "")}</td>
        <td>Board Is Dark:</td><td>${(board.dark ? "Yes" : "No")}</td>
    </tr>

    <tr><td>Re-enter When Zapped:</td><td>${(board.zap ? "Yes" : "No")}</td>
        <td>Re-enter X/Y:</td><td>${board.enter_x} / ${board.enter_y}</td>
    </tr>
    <tr><td>Time Limit:</td>
        <td>${board.time_limit ? board.time_limit + " sec"+(board.time_limit != 1 ? "s" : "") : "None"}.</td>
        <td colspan="2">&nbsp;</td>
    </tr>
    <tr>
        <td>Stat Elements:</td><td>${board.stat_count + 1} / 151</td>
        <td>Board Size:</td><td>${board.size} bytes</td>
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
        if (board[props[idx]] != 0 && board[props[idx]] != null)
        {
            if (world.boards[board[props[idx]]])
                var displayed_title = world.boards[board[props[idx]]].title;
            else
                var displayed_title = `Undefined Board ${board[props[idx]]}`;
            output += `<td><a class="board-link" data-direction="${props[idx]}" data-board="${board[props[idx]]}" href="?file=${loaded_file}&board=${board[props[idx]]}">${board[props[idx]]}. ${displayed_title}</a></td>`;
        }
        else
            output += `<td>None</td>`;
        if (idx % 2 != 0)
            output += `</tr>`;
    }

    output += `</table>`;

    // Tools
    if (can_live_edit)
        output += `<br><input type="button" id="play-board" value="Play This Board">`;

    $("#board-info").html(output);
    tab_select("board-info");

    // Bind board links
    $(".board-link").click(switch_board);

    // Bind play-board link
    $("#play-board").click(play_board);

    // Render the stat info as well
    render_stat_list();
    return true;
}

function draw_board()
{
    set_active_envelope("canvas");

    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = "black";
    ctx.fillRect(0,0,CANVAS_WIDTH,CANVAS_HEIGHT);
    var board_number = $(".board.selected").data("board-number") || 0;
    if (board_number == null)
        return false;

    var board = world.boards[board_number];

    renderer.render(board);
    $("#world-canvas").click(stat_info);
    $("#world-canvas").dblclick({"board": board}, passage_travel);

    // Click coordinates in hash
    if (hash_coords)
    {
        var sliced = hash_coords.slice(1);
        var split = sliced.split(",");
        var e = {"data":{"x":split[0], "y":split[1], "idx":-1}};
        if (split[2])
            e["data"]["idx"] = split[2];
        stat_info(e);
    }
}

function passage_travel(e) {
    // Calculate position on canvas
    var rect = canvas.getBoundingClientRect();
    var raw_x = e.pageX - rect.left - document.querySelector("html").scrollLeft;
    var raw_y = e.pageY - rect.top - document.querySelector("html").scrollTop;

    // Calculate ZZT tile
    var x = parseInt(raw_x / (TILE_WIDTH * SCALE)) + 1;
    var y = parseInt(raw_y / (TILE_HEIGHT * SCALE)) + 1;
    var tile_idx = ((y-1) * ENGINE.board_width) + (x-1);

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
        // Calculate position on canvas
        var rect = canvas.getBoundingClientRect();
        var raw_x = e.pageX - rect.left - document.querySelector("html").scrollLeft;
        var raw_y = e.pageY - rect.top - document.querySelector("html").scrollTop;

        // Calculate ZZT tile
        var x = parseInt(raw_x / (TILE_WIDTH * SCALE)) + 1;
        var y = parseInt(raw_y / (TILE_HEIGHT * SCALE)) + 1;
        var tile_idx = ((y-1) * ENGINE.board_width) + (x-1);
        var stat_idx = -1 // Sentinel to just use first match
    }
    else
    {
        var x = e.data.x;
        var y = e.data.y;
        var stat_idx = e.data.idx;
    }

    var tile_idx = ((y-1) * ENGINE.board_width) + (x-1);
    var hash_coords = "#" + x + "," + y;

    if (stat_idx != -1)
        hash_coords += "," + stat_idx;

    //window.location.hash = ;
    history.replaceState(undefined, undefined, hash_coords)

    // Get the current tile
    if (tile_idx < 0 || tile_idx >= ENGINE.tile_count)
    {
        // Use a stub element for out-of-bounds stats
        var tile = {
            "id":0,
            "tile":tile_idx,
            "name":"Out of bounds",
            "character":63, // "?"
            "color_id":0,
            "foreground":0,
            "background":0,
        }
    }
    else
    {
        var tile = world.boards[board_number].elements[tile_idx];
        console.log("TILE INFO");
        console.log(tile);
    }

    // Iterate over stat elements
    var stat = null;
    for (var idx = 0; idx < world.boards[board_number].stats.length; idx++)
    {
        if (world.boards[board_number].stats[idx].x == x && world.boards[board_number].stats[idx].y == y)
        {
            stat = world.boards[board_number].stats[idx];
            if ((stat_idx == -1) || (stat_idx == world.boards[board_number].stats[idx].idx))
            {
                stat_idx = idx;
                break;
            }
        }
    }

    var output = `<table class="fv">
    <tr>
        <th>Position</td>
        <td>(${x}, ${y}) [${tile_idx}/${ENGINE.tile_count}]</td>
        <th>Default Character</td>
        <td>${tile.character}</td>
    </tr>
    <tr>
        <th>Name</td>
        <td>${tile.name}</td>`

    if (stat != null)
        output += `<th>Cycle</td><td>${stat.cycle}</td>`;
    else
        output += `<td>&nbsp;</td><td>&nbsp;</td>`;

    output += `</tr>
    <tr>
        <th>ID</td>
        <td>${tile.id}</td>
        <th>Color</td>
        <td>${color_desc(tile.color_id)}</td>
    </tr>
    `;

    if (stat != null)
    {
        var p1name = (ELEMENTS[tile.id].hasOwnProperty("param1") ? ELEMENTS[tile.id].param1 : "Param1");
        var p2name = (ELEMENTS[tile.id].hasOwnProperty("param2") ? ELEMENTS[tile.id].param2 : "Param2");
        var p3name = (ELEMENTS[tile.id].hasOwnProperty("param3") ? ELEMENTS[tile.id].param3 : "Param3");
        var param1_display = stat.param1;
        var param2_display = stat.param2;
        var param3_display = stat.param3;

        if (tile.name == "Passage")
        {
            var loaded_file = $("#file-list ul > li.selected").contents().filter(function(){ return this.nodeType == 3; })[0].nodeValue;
            if (world.boards[stat.param3])
            {
                param3_display = `<a class="board-link" data-board="${stat.param3}" href="?file=${loaded_file}&board=${stat.param3}">${stat.param3} - ${world.boards[stat.param3].title}</a>`;
            }
            else
            {
                param3_display = `${stat.param3} - <i>Out of bounds board</i>`;
            }
        }

        if (tile.name == "Spinning Gun" || tile.name == "Tiger")
        {
            var rate_value = stat.param2;
            var projectile = "Bullets";
            if (stat.param2 >= 128)
            {
                rate_value = stat.param2 - 128;
                projectile = "Stars";
            }
            param2_display = `${rate_value} [${projectile}] (Raw: ${stat.param2})`;
        }

        output += `
        <tr>
            <th>Under ID</th><td>${ELEMENTS[stat.under_id].name}</td>
            <th>Under Color</th><td>${color_desc(stat.under_color)}</td>

        </tr>
        <tr>
            <th>${p1name}</th><td>${param1_display}</td>
            <th>X/Y-Step</th><td>(${stat.x_step}, ${stat.y_step}) ${stat.direction}</td>
        </tr>
        <tr>
            <th>${p2name}</th><td>${param2_display}</td>
            <th>Leader</th><td>${stat.leader}</td>
        </tr>
        <tr>
            <th>${p3name}</th><td>${param3_display}</td>
            <th>Follower</th><td>${stat.follower}</td>
        </tr>
        <tr>`

        // Pre-bound stat / OOP Length
        var oop_length_text = stat.oop_length;
        if (stat.oop_length < 0)
        {
            output += `<th>Bound Stat</th><td>${Math.abs(stat.oop_length)}`;
        }
        else
        {
            output += `<th>OOP Length</th><td>${oop_length_text}</td>`;
        }
        output += `<th>Instruction</th><td>${stat.oop_idx}</td></tr>
        </table>

        ZZT-OOP style:
        <label><input type="radio" name="oop_style" value="modern"${oop_style == 'modern' ? ' checked' : ''}> Modern</label>
        <label><input type="radio" name="oop_style" value="zzt-scroll"${oop_style == 'zzt-scroll' ? ' checked' : ''}> Classic</label>

        <div id="oop-wrapper"><code id='zzt-oop' class='${ENGINE.name == 'Super ZZT' ? 'super-' : ''}zzt-oop ${oop_style}' data-stat_idx='${stat_idx}'></code></div>
        `;
    }

    $("#element-info").html(output);
    render_zzt_oop(stat);
    tab_select("element-info");
    // Bind board links (from passages)
    $(".board-link").click(switch_board);
    // Bind radio buttons
    $("input[name=oop_style]").click(function (){
        oop_style = $(this).val();
        render_zzt_oop(null);
    });

    return true;
}

function tab_select(selector)
{
    $("#file-data > div").hide();
    $("#file-tabs div").removeClass("selected");
    $("div[name=zip-info]").removeClass("selected");
    $("div[name="+selector+"]").addClass("selected");
    $("#"+selector).show();
}

$(window).bind("load", function() {
    $("#local-load").click(load_local_file);

    $("#file-list li").click({"format": "auto"}, pull_file);
    $("#file-tabs div").click(function (){tab_select($(this).attr("name"))});
    $("#zip-name").click(function (){tab_select($(this).attr("name"))});

    // Stat sorting
    $("select[name=stat-sort]").change(render_stat_list);

    $("select[name=charset]").change(load_charset);
    $("input[name=2x]").change(load_charset);

    // Renderer
    $("select[name=renderer]").change(function (){
        renderer.render = renderer[$(this).val()];
        $("li.selected.board").click();
        tab_select("preferences");
    });

    // Invisibles, Monitors, Board Edges, and Statless Objects
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
    $("select[name=statlessobj]").change(function (){
        renderer.statlessobj_style = $(this).val();
        renderer.render(world.boards[board_number]);
    });

    // High Intensity BGs
    $("select[name=intensity]").change(function (){
        renderer.bg_intensity = $(this).val();
        renderer.render(world.boards[board_number]);
    });

    // Scale
    $("input[name=pref-board-scale]").change(function (){
        update_scale();
    });

    // Keyboard Shortcuts
    $(window).keyup(function (e){
        var match;
        if ($("input[name=q]").is(":focus") || $("input[name=code-search]").is(":focus"))
            return false;

        if (! e.shiftKey && (e.keyCode == KEY.NP_PLUS || e.keyCode == KEY.PLUS || e.keyCode == KEY.J)) // Next Board
        {
            // Need to iterate over these until a non-hidden one is found.
            if (match = $(".board.selected").nextAll(".board"))
                match[0].click();
        }
        else if (! e.shiftKey && (e.keyCode == KEY.NP_MINUS || e.keyCode == KEY.MINUS || e.keyCode == KEY.K)) // Previous Board
        {
            if (match = $(".board.selected").prevAll(".board"))
                match[0].click();
        }
        else if (e.keyCode == KEY.W) // World
            $("div[name=world-info]").click();
        else if (! e.shiftKey && e.keyCode == KEY.B) // Board
            $("div[name=board-info]").click();
        else if (e.keyCode == KEY.E) // Element
            $("div[name=element-info]").click();
        else if (e.keyCode == KEY.S) // Stat
            $("div[name=stat-info]").click();
        else if (e.keyCode == KEY.P) // Prefs.
            $("div[name=preferences]").click();
        else if (e.keyCode == 104 && $("a.board-link[data-direction=exit_north]")) // Board to North
                $("a.board-link[data-direction=exit_north]").click();
        else if (e.keyCode == 98 && $("a.board-link[data-direction=exit_south]")) // Board to South
                $("a.board-link[data-direction=exit_south]").click();
        else if (e.keyCode == 102 && $("a.board-link[data-direction=exit_east]")) // Board to East
                $("a.board-link[data-direction=exit_east]").click();
        else if (e.keyCode == 100 && $("a.board-link[data-direction=exit_west]")) // Board to West
                $("a.board-link[data-direction=exit_west]").click();
        else if (e.shiftKey && e.keyCode == KEY.B) // Toggle blinking
        {
            var cur = $("#pref-intensity").val();
            var now = (cur == "low" ? 'high' : 'low');
            $("#pref-intensity").val(now);
            $("select[name=intensity]").change();
        }

        // File navigation
        if (e.shiftKey && (e.keyCode == KEY.NP_PLUS || e.keyCode == KEY.PLUS || e.keyCode == KEY.J)) // Next
        {
            if (match = $(".zip-content.selected").nextAll(".zip-content"))
                match[0].click();
        }
        else if (e.shiftKey && (e.keyCode == KEY.NP_MINUS || e.keyCode == KEY.MINUS || e.keyCode == KEY.K)) // Previous
        {
            if (match = $(".zip-content.selected").prevAll(".zip-content"))
                match[0].click();
        }
    });

    // History
    $(window).bind("popstate", function(e) {
        /*
        console.log("POPSTATE", history.state);
        console.log("FILENAME CURRENT", filename);
        console.log("BOARD CURRENT", board_number);
        */
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

    // Initialize the overlay
    $("#fv-left-sidebar").html(overlay.html_template);
    $("#world-canvas").mousemove(function (e){overlay.update(e)});
    $("#world-canvas").mouseout(overlay.hide);

    // Activate the file viewer
    init();
});

/* Auto Load functions */
function auto_load()
{
    console.log("Auto Load:", load_file);
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

    while (idx < data.length)
    {
        // Read the first byte for length of name
        var name_length = read(data, 1, idx);
        idx += 2;

        var name = str_read(data, 50, idx).substr(0,name_length);
        idx += 100;

        var score = read(data, 2, idx);
        idx += 4;

        var spaced_score = "     " + score
        spaced_score = spaced_score.slice(-5);
        scores.push({"name":name, "score":score, "spaced_score":spaced_score});

        if (scores.length >= 30)
            break;
    }
    return scores;
}

function parse_szzt_scores(data)
{
    var scores = [];
    var idx = 0;
    while (idx < data.length)
    {
        // Read the first byte for length of name
        var name_length = read(data, 1, idx);
        idx += 2;

        if (name_length == 0)
            break;

        var name= str_read(data, 15, idx).substr(0,name_length);
        idx += 120;

        var score = read(data, 2, idx);
        idx += 4;

        var spaced_score = "     " + score
        spaced_score = spaced_score.slice(-5);
        scores.push({"name":name, "score":score, "spaced_score":spaced_score});

        if (scores.length >= 30)
            break;
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
    var selected_charset = $("select[name=charset]").val();

    if ($("#world-canvas").length == 0)
        var no_canvas = true;
    else
        var no_canvas = false;

    // Charset needs to be loaded and/or canvas doesn't exist
    if (CHARSET_NAME != selected_charset || no_canvas)
    {
        console.log("Loading charset", selected_charset);
        CHARSET_NAME = selected_charset;
        CHARSET_IMAGE = new Image();
        CHARSET_IMAGE.src = "/static/images/charsets/"+CHARSET_NAME;
        CHARSET_IMAGE.addEventListener("load", function ()
        {
            CANVAS_WIDTH = CHARSET_IMAGE.width / 16 * ENGINE.board_width;
            CANVAS_HEIGHT = CHARSET_IMAGE.height / 16 * ENGINE.board_height;

            TILE_WIDTH = CANVAS_WIDTH / ENGINE.board_width;
            TILE_HEIGHT = CANVAS_HEIGHT / ENGINE.board_height;

            canvas = document.getElementById("world-canvas");
            ctx = canvas.getContext("2d", { alpha: true });

            draw_board();
        });
    }
    else
    {
        draw_board();
    }
}

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
    }
    return oop.join("\n");
}

function render_stat_list()
{
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
            if (a.tile_idx == -61)
                var stat_name1 = "Messenger(?)";
            else
            {
                if (a.tile_idx >= world.boards[board_number].elements.length || a.tile_idx < 0)
                    var stat_name1 = "Out of bounds stat";
                else
                    var stat_name1 = world.boards[board_number].elements[a.tile_idx].name;
            }
            if ((stat_name1 == "Scroll" || stat_name1 == "Object") && a.oop[0] == "@")
                stat_name1 = a.oop.slice(0, a.oop.indexOf("\r"));

            if (b.tile_idx == -61)
                var stat_name2 = "Messenger(?)";
            else
            {
                if (b.tile_idx >= world.boards[board_number].elements.length || b.tile_idx < 0)
                    var stat_name2 = "Out of bounds stat";
                else
                    var stat_name2 = world.boards[board_number].elements[b.tile_idx].name;
            }
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

        // Out of bounds stat check
        if ((stat.tile_idx < 0) || (stat.tile_idx >= ENGINE.tile_count))
        {
            if (stat.tile_idx == -61)
                var stat_name = "Messenger(?)";
            else
                var stat_name = "Out of bounds stat";
        }
        else
        {
            var stat_name = board.elements[stat.tile_idx].name;
        }

        if ((stat_name == "Scroll" || stat_name == "Object") && stat.oop[0] == "@")
            stat_name = stat.oop.slice(0, stat.oop.indexOf("\r"));

        if (stat.oop.length == 0)
            stat_list += `<li class='empty'>`;
        else
            stat_list += `<li>`;
        stat_list += `
            <a class='jsLink' name='stat-link' data-x='${stat.x}' data-y='${stat.y}' data-idx='${stat.idx}'>
            (${("00"+stat.x).slice(-2)}, ${("00"+stat.y).slice(-2)}) [${(("0000"+(stat.tile_idx+1)).slice(-4))}]
            ${stat_name}</a> `;
        if (stat.oop.length)
                stat_list += `${stat.oop.length} bytes`;
            stat_list += `</li>\n`;
    }
    $("#stat-info ol").html(stat_list);
    $("a[name=stat-link]").click(function (){
        var e = {"data":{"x":$(this).data("x"), "y":$(this).data("y"), "idx":$(this).data("idx")}};
        stat_info(e);
    });

    $("a[name=stat-link]").hover(function (){
        highlight($(this).data("x"), $(this).data("y"));
    }, function (){
        unhighlight($(this).data("x"), $(this).data("y"));
    });

    $("#stat-toggle").off("click").click(function (){
        if ($(this).hasClass("activated")) // Redisplay
            $("#stat-info li.empty").css({"visibility": "visible", "height":"auto"});
        else // Hide
            $("#stat-info li.empty").css({"visibility": "hidden", "height":0});
        $(this).toggleClass("activated");

    });
    return true;
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
        var formatted_title = world.boards[x].title ? world.boards[x].title.replace(/</g, "&lt;").replace(/>/g, "&gt;") : `-untitled`;
        board_list += `
            <div name='board_idx'>${formatted_num}.</div>
            <div name='board_name'><pre>${formatted_title}</pre></div>
        `;

        if (world.starting_board == x)
            board_list += `</b>`;
        board_list += `</li>\n`;
    }
    board_list += `</ol><br>\n`;
    return board_list;
}

function code_search()
{
    var query = $("input[name=code-search]").val().toLowerCase();
    var board_matches = [];
    var coordinate_matches = {};

    if (! query)
        return false;

    for (var board in world.boards)
    {
        for (var stat in world.boards[board].stats)
        {
            // Check all stats that have ZZT-OOP
            if (world.boards[board].stats[stat].oop && (world.boards[board].stats[stat].oop.toLowerCase().indexOf(query) != -1))
            {
                // Log the matching board if it hasn't been logged yet
                if (board_matches.indexOf(board) == -1)
                {
                    board_matches.push(parseInt(board));
                }

                // Log the stat's coordinates
                if (! coordinate_matches[board])
                    coordinate_matches[board] = [world.boards[board].stats[stat].x + "," + world.boards[board].stats[stat].y];
                else
                    coordinate_matches[board].push(world.boards[board].stats[stat].x + "," + world.boards[board].stats[stat].y);
            }
        }
    }

    if (! board_matches) // No results
        return false;

    $(".code-match").remove();

    $("#file-list .selected ol").children().filter("li").each(function (){
        $(this).show(); // Reveal boards to allow multiple searches
        if (board_matches.indexOf($(this).data("board-number")) != -1)
        {
            //console.log("Match on" + $(this).text());
            for (var match_idx = 0; match_idx < coordinate_matches[$(this).data("board-number")].length; match_idx++)
            {
                var match_name = coordinate_matches[$(this).data("board-number")][match_idx];
                var x = match_name.split(",")[0];
                var y = match_name.split(",")[1];
                var tile_idx = parseInt((y - 1) * 60) + parseInt(x);

                var stat_name = world.boards[$(this).data("board-number")].elements[tile_idx - 1].name;
                var stats = world.boards[$(this).data("board-number")].stats
                for (var stat_idx = 0; stat_idx < stats.length; stat_idx++)
                {
                    if (stats[stat_idx].x == x && stats[stat_idx].y == y)
                    {
                        if ((stat_name == "Scroll" || stat_name == "Object") && stats[stat_idx].oop[0] == "@")
                        {
                            stat_name = stats[stat_idx].oop.slice(0, stats[stat_idx].oop.indexOf("\r"));
                        }
                        var oop_size = stats[stat_idx].oop_length;
                        break;
                    }
                }

                $(this).after(`<li class='code-match' data-board-number="" data-x="${x}" data-y="${y}">⤷(${x}, ${y}) [${(("0000"+(tile_idx)).slice(-4))}] ${stat_name} ${oop_size} bytes</li>`);
            }
        }
        else // Hide boards that don't match?
        {
            $(this).hide();
        }
    });

    // Bind the matches to click
    $(".code-match").click(function (event){
        event.stopPropagation();
        $(this).prev().click();
        var e = {"data":{"x":$(this).data("x"), "y":$(this).data("y")}};
        stat_info(e);
        // HERE
    });

    console.log("Matches:", board_matches);
}

function code_search_reset()
{
    $("#file-list .selected ol").children().filter("li").show();
    $("li.code-match").remove();
}

function show_unterminated()
{
    $(this).hide();
    $("#world-info .fv-hidden").show();
    $("#world-info .fv-hidden-row").css("display", "table-row");
}

function bind_world_widgets()
{
    $("#code-search-submit").click(code_search);
    $("#code-search-reset").click(code_search_reset);
    $("#show-unterminated").click(show_unterminated);
    return true;
}

function int_to_char(number)
{
    return String.fromCharCode(CP437_TO_UNICODE[number]);
}

function play_board()
{
    var scale = 1;
    var base_w = 640;
    var base_h = 350;
    var live_url = "/play/"+letter+"/"+key+"?player=zeta&mode=popout&scale=" + scale + "&live=1&world="+filename+"&start=" +board_number;
    window.open(live_url, "popout-"+key, "width="+(base_w * scale)+",height="+(base_h * scale)+",toolbar=0,menubar=0,location=0,status=0,scrollbars=0,resizable=1,left=0,top=0");
}

function render_zzt_oop(stat)
{
    if (stat == null)
    {
        stat = world.boards[board_number].stats[$("#zzt-oop").data("stat_idx")];
    }

    $("#zzt-oop, #oop-wrapper").removeClass("modern zzt-scroll");
    $("#oop-wrapper").addClass(oop_style);
    $("#oop-wrapper .name").remove();

    if (oop_style == "zzt-scroll")
    {
        $("#oop-wrapper").prepend("<div class='name'>Edit Program</div>");
        $("zzt-oop").addClass("content");
    }
    else
    {
        $("zzt-oop").removeClass("content");
    }

    if (stat && oop_style == "modern")
        $("#zzt-oop").html(syntax_highlight(stat.oop));
    else if (stat)
        $("#zzt-oop").html(stat.oop);

    if (! stat || stat.oop_length == 0)
        $("#zzt-oop").hide();
    else
        $("#zzt-oop").show();
}

function set_active_envelope(envelope)
{
    if ($("#"+envelope+"-envelope").hasClass("active"))
        return true;

    $(".output.active").removeClass("active");
    $("#fv-main").scrollTop(0);
    $(".output." + envelope).addClass("active");
}

function update_scale()
{
    SCALE = document.querySelector("input[name=pref-board-scale]").checked ? 2 : 1;
    $("#world-canvas").css("width", CANVAS_WIDTH * SCALE + "px");
    $("#world-canvas").css("height", CANVAS_HEIGHT * SCALE + "px");

    // If you shrink, snap the upper canvas area size
    if (SCALE == 1)
        $("#fv-main").css("height", "auto");

    // Set scale cookie
    var now = new Date();
    var time = now.getTime();
    var expireTime = time + (1000 * 31536000); // 1yr
    now.setTime(expireTime);
    document.cookie = `file_viewer_scale=${SCALE};expires=${now.toGMTString()};path=/;SameSite=Strict`;
}

function color_desc(color)
{
    return COLOR_NAMES[color % 16] + " on " + COLOR_NAMES[Math.floor(color / 16)] + ` (${color})` ;
}

function identify_save_type(data)
{
    var file_identifier = read(data, 2, 0);

    if (file_identifier == engines["zzt"]["identifier"])
        return "zzt";
    else if (file_identifier == engines["szt"]["identifier"])
        return "szt";
    else
        return null;
}

function step_direction(x, y)
{
    var vector = [x, y].toString();
    var directions = {
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
    var output = directions[vector];
    if (output == undefined)
        return "";
    return output;
}

function signed(i)
{
    if (i > 32767)
        return i - 65536;
    return i;
}

function close_file(f)
{
    f.removeClass("selected");
    f.find("ol").remove();
}
