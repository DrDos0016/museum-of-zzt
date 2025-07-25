"use strict";

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

var IS_SEARCHING = false;

$(document).ready(function (){
    // New Screenshot Zoom
    $(".zoomable").click(function (){
        $(this).toggleClass("thumbnail zoomed");
    });

    // Set initial zoom
    if (global_zoomed_state)
        $(".zoomable").click();

    // Browse Letters Select-based Input
    $("#letter-button").click(function (){
        var url = $("#letter-select").val().toLowerCase();
        if (url)
            window.location = url;
    });

    // Reload on sort change
    $(".sort-methods select[name='sort']").change(function (){
        var qs = window.location.search; // Query string
        if (qs == "")
            window.location = "?sort="+$(this).val();
        else
        {
            qs = "&" + qs.slice(1);
            var params = qs.split("&").slice(1);
            var new_qs = "?";

            for (var idx in params)
            {
                var key = params[idx].split("=")[0];
                var val = params[idx].split("=")[1];

                if (key == "sort")
                    new_qs += key + "=" + $(this).val();
                else if (key == "page")
                    new_qs += "page=1";
                else
                    new_qs += key + "=" + val;
                new_qs += "&";
            }
            new_qs = new_qs.slice(0, -1);

            // Make sure there's a sort param
            if (new_qs.indexOf("sort=") == -1)
                new_qs += "&sort="+$(this).val();

            window.location = window.location.pathname + new_qs;
        }
    });

    // Content warnings
    if (document.cookie.replace(/(?:(?:^|.*;\s*)hide_content_warnings\s*\=\s*([^;]*).*$)|^.*$/, "$1") == 1)
    {
        $(".content-warning").hide();
    }

    $("span[name=cw-hide-this]").click(function (){
        $(this).parent().parent().parent().hide();
    });

    $("span[name=cw-hide-all]").click(function (){
        $(".content-warning").hide();
        var now = new Date();
        var time = now.getTime();
        var expireTime = time + (1000 * 31536000); // 1yr
        now.setTime(expireTime);
        document.cookie = "hide_content_warnings=1;expires=" + now.toGMTString() + ";path=/";
    });

    // Light/Dark Theme Toggle
    $("#toggle-light-dark-theme").click(function (){
        let theme = $("body").hasClass("theme-dark") ? "light" : "dark";
        ajax_set_setting("theme", theme, update_theme);
    });


    // Zoom all
    $("#toggle-zoom").click(function (){
        global_zoomed_state = ! global_zoomed_state;
        let on_off = global_zoomed_state ? "on" : "off";
        ajax_set_setting("prezoom", on_off, function (){});
        if (global_zoomed_state)
            $(".zoomable").not(".zoomed").click();
        else
            $(".zoomable.zoomed").click();
    });

    // Expand/Contract Middle Column
    $("#expand-contract").click(function (){
        let sidebars = $("body").hasClass("expanded") ? "show" : "hide";
        ajax_set_setting("sidebars", sidebars, expand_contract_middle_column);
        if (sidebars == "show")
            $(".sidebar").css({"display": "", "left": "", "right": ""});
    });

    // File association selection
    $("#alt-file-listing").change(function (){
        if ($(this).val() == "Browse-Associated")
        {
            let slug = $("article").data("article-slug");
            window.location = "/file/browse/article/" + slug;
            return true;
        }
        window.location = "?alt_file=" + $(this).val();
    });

    $("code.zzt-oop").each(function (){
        var raw = $(this).text();
        var processed = syntax_highlight(raw);
        $(this).html(processed);
    })

    // Explicit Download Warning
    $(".download-link.explicit").click(function (e){
        var explicit_warning = "This file is known to contain content not suitable for minors.\n\nPress 'OK' to confirm that you are of age to download such content and wish to do so.";
        if (! confirm(explicit_warning))
            e.preventDefault();
    });

    // Change pages via select input
    $("select[name=page-selector]").change(function (){
        var params = $(this).data("params");
        var dest = "?page=" + $(this).val() + params;
        window.location = dest;
    });

    // Spoiler text
    $(".spoiler").click(function (){
        $(this).toggleClass("revealed");
    });

    // Search suggestions
    $("input[name=q]").bind("input", function (){
        clearTimeout($(this).data("timeout"));
        setTimeout(pre_search, 200);
    });

    // Review Profanity Filter
    $("input[name=review-profanity-filter]").change(function (){
        var val = $(this).val();
        var qs = window.location.search; // Query string
        if (qs == "")
            window.location = "?pf="+$(this).val();
        else
            window.location = window.location.pathname + qs + "&pf="+$(this).val();
    });

    // Resize Youtube Livestream embeds
    //resize_yt_embed();

    // Simple input attributes
    $("input[data-click-select]").click(function (){$(this).select();});
    $("textarea[data-click-select]").click(function (){$(this).select();});

    // Burger
    $(".hamburger-menu-button").click($(this), toggle_burger);

    // WIP
    init_expandable_model_block_fields();

});

function toggle_burger(e)
{
    // Get current menu state
    var src = $(e.target);
    var alt = (src.attr("id") == "left-hamburger") ? $("#right-hamburger") : $("#left-hamburger");
    var current_state = src.data("state");

    // Toggle open to closed and vice versa
    if (current_state == "open")
    {
        src.data("state", "closed");
        close_burger(src);
    }
    else
    {
        open_burger(src);
        alt.data("state", "closed");
        close_burger(alt);
    }
}

function open_burger(src)
{
    src.addClass("ega-yellow");
    src.removeClass("ega-white");
    src.data("state", "open");
    var direction = (src.attr("id") == "left-hamburger" ? "left" : "right");
    var new_css = {};
    new_css[direction] = "0%";
    var target = $(src.data("target"));
    target.css({"display": "flex"});
    target.animate(new_css, 150, "linear", function (){});
}

function close_burger(src)
{
    src.addClass("ega-white");
    src.removeClass("ega-yellow");
    src.data("state", "closed");
    var direction = (src.attr("id") == "left-hamburger" ? "left" : "right");
    var new_css = {};
    new_css[direction] = "-100%";
    var target = $(src.data("target"));
    target.animate(new_css, 150, "linear", function (){
        target.hide();
    });
}

function pre_search()
{
    var query = $("input[name=q]").val();
    if (! query)
        return false;

    $.ajax({
        url:"/ajax/get-search-suggestions/",
        data:{
            "q":query,
        }
    }).done(function (data){
        var output = "";
        for (var idx in data["suggestions"])
        {
            output += '<option value="'+data["suggestions"][idx]+'">';
        }
        $("#search-suggestions").html(output);
        $("input[name=q]").focus();
    });
};

// ZZT-OOP Syntax highlighting
function syntax_highlight(oop)
{
    var oop = oop.split("\n");
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

function int_to_char(number)
{
    return String.fromCharCode(CP437_TO_UNICODE[number]);
}

function filesize_format(bytes)
{
    if (bytes == 0)
        return "0 B";
    var i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(1) * 1 + ' ' + ['B', 'KB', 'MB', 'GB', 'TB'][i];
}

function resize_yt_embed()
{
    if ($("article.livestream iframe").length == 0)
        return false;

    var width = $("article.livestream iframe").width()
    if (width == 640) // 4:3 videos
    {
        var ratio = 1.3333;
        var max_width = 640;
    }
    else // 16:9 videos
    {
        var ratio = 1.7778;
        var max_width = 1920;
    }

    var new_width = $("article.livestream").width() - 20;

    if (new_width >= max_width)
        new_width = max_width;

    var new_height = parseInt(Math.round(new_width / ratio));
    $("article.livestream iframe").width(new_width);
    $("article.livestream iframe").height(new_height);
}

function expand_field()
{
    if ($(this).data("expanded") == "1")
    {
        $(this).data("expanded", "0");
        $(this).html("Show All");
    }
    else
    {
        $(this).data("expanded", "1");
        $(this).html("Show Some");
    }
    $(this).parent().next(".value").toggleClass("expanded");
}

function init_expandable_model_block_fields()
{
    $(".model-block-data .datum .value").each(function (){
        if ($(this)[0].scrollHeight > $(this)[0].clientHeight && $(this).prev(".label").length)
        {
            let original = $(this).prev(".label").html();
            let additional = "<div class='field-expand-button'>Show All</div>";
            $(this).prev(".label").html(original + additional);
        }
    });
    $(".field-expand-button").click(expand_field);
}

function expand_contract_middle_column(data=null)
{
    let arrows = $("#expand-contract").html();
    //$(".sidebar, #top-links, #logo-area").toggle();
    $("body").toggleClass("expanded");
    $("#expand-contract").html(arrows[2] + arrows[1] + arrows[0]);
}

function update_theme(data=null)
{
    $("body").toggleClass("theme-dark");
}

function ajax_set_setting(key, value, callback)
{
    $.ajax({
        url:"/action/set-setting/",
        data:{
            "setting": key + "|" + value,
        }
    }).done(function (data){
        callback(data);
    });
}

/* ZZM/#Play */
let ZZM_WIDGETS = [];

class Museum_ZZM_Audio_Player
{
    constructor(raw, source_element, mutable, widget) {
        if (! mutable)
            this.play_commands = this.clean_raw_data(raw);
        else
            this.play_commands = "x";
        this.mutable = mutable;
        this.volume = 1.0 * source_element.parent().find(".zzmplay-volume").val();
        this.pre_mute_volume = this.volume;
        this.source_element = source_element;
        this.source = null;
        this.playing = false;
        this.play_button = null;
        this.gainNode = null;
        this.ctx = null;
        this.data = null; // Actual audio data that gets played after parsing
        this.parsed = false;
        this.timer = null;
        this.widget_idx = null;
        this.start_offset_ms = 0;
        this.widget = widget;
        this.prefix_required = true;
    }

    clean_raw_data(raw)
    {
        raw = raw.replaceAll("#bgplay", "#play");
        raw = raw.replaceAll("#fgplay", "#play");
        let cleaned = raw.replaceAll(/^(?!#play).*$/gm, "");
        cleaned = cleaned.replaceAll("#play ", "");
        cleaned = cleaned.replaceAll("\n\n", "\n");
        cleaned = cleaned.trim();
        return cleaned;
    }

    update_play_commands()
    {
        let raw = this.source_element.val();
        console.log("To... " + raw);
        if (this.prefix_required)
            this.play_commands = this.clean_raw_data(raw);
        else
            this.play_commands = raw;

        if (this.mutable)
        {
            this.update_composition_url();
        }
        return true;
    }

    delay(ms) {
        return new Promise(res => {
            setTimeout(() => { res('') }, ms);
        });
    }

    async play() {
        if (this.source) {
            this.stop();
        }

        if (this.mutable)
            this.update_play_commands();

        this.ctx = new AudioContext();
        const sampleRate = this.ctx.sampleRate; // audio context's sample rate

        // Generate the square wave data
        if (! this.data || this.mutable)
        {
            this.data = new Float32Array();
            this.play_button.html("Wait");
            this.play_button.prop("disabled", "disabled");
            await this.delay(250);

            let play_command_list = this.play_commands.split("\n");
            for (let idx in play_command_list)
            {
                let buffer = await parseSound(play_command_list[idx], sampleRate);
                this.data = f32ArrayConcat(this.data, buffer)
            }
        }

        // Create an AudioBuffer
        if (this.data.length == 0)
        {
            this.play_button.html("#Play");
            this.play_button.prop("disabled", "");
            return false;
        }
        const audioBuffer = this.ctx.createBuffer(1, this.data.length, sampleRate);

        // Fill the buffer with the square wave data
        const channelData = audioBuffer.getChannelData(0);
        channelData.set(this.data);

        // Create an AudioBufferSourceNode
        this.source = this.ctx.createBufferSource();
        this.source.buffer = audioBuffer;

        // Create GainNode (Volume Control)
        this.gainNode = this.ctx.createGain()
        this.gainNode.gain.value = this.volume;
        this.gainNode.connect(this.ctx.destination);

        // Connect the source to the context's destination
        this.source.connect(this.gainNode);

        var scope = this;
        this.source.addEventListener("ended", function (){
            scope.stop();
            let max_pos = scope.source_element.parent().find(".zzmplay-seek").attr("max");
            scope.seek(0);
            scope.source_element.parent().find(".progress").html("00:00");
        });

        // Set duration
        let duration_val = this.source_element.parent().find(".duration").text();
        if (this.mutable || duration_val == "--:--")
        {
            this.source_element.parent().find(".duration").html(this.format_time(this.source.buffer.duration));
            this.source_element.parent().find(".zzmplay-seek").val(0);
            this.source_element.parent().find(".zzmplay-seek").attr("max", Math.ceil(this.source.buffer.duration) * 1000);
        }

        // Start playback
        this.play_button.html("#End");
        this.play_button.prop("disabled", "");
        this.source.start(0, parseInt(this.start_offset_ms / 1000));
        this.timer = setInterval(update_playback_time, 500, this.widget_idx);
        this.playback_start_time = Date.now();
        this.playing = true;
        this.widget.addClass("playing");

    }

    format_time(seconds)
    {
        let m = ("0" + parseInt(Math.ceil(seconds) / 60)).slice(-2);
        let s = ("0" + parseInt(Math.ceil(seconds) % 60)).slice(-2);
        return `${m}:${s}`;
    }

    stop(reset_seek_bar)
    {
        this.source.stop();
        this.widget.removeClass("playing");
        clearInterval(this.timer);
        this.playing = false;
        this.play_button.html("#Play");
        if (reset_seek_bar)
            this.source_element.parent().find(".zzmplay-seek").val(0);
        this.playback_start_time = null;
    }

    play_pause(button)
    {
        if (! this.play_button)
            this.play_button = button;

        if (this.playing)
        {
            this.stop();
        }
        else
        {
            this.play();
        }
    }

    toggle_mute()
    {
        let cur_vol = this.source_element.parent().find(".zzmplay-volume").val();
        if (cur_vol != 0)
        {
            this.pre_mute_volume = cur_vol;
            this.source_element.parent().find(".zzmplay-volume").val(0);
            this.set_volume(0);
        }
        else
        {
            this.source_element.parent().find(".zzmplay-volume").val(this.pre_mute_volume);
            this.set_volume(this.pre_mute_volume);
        }
    }

    toggle_source(current)
    {
        this.source_element.toggleClass("show");
    }

    set_volume(volume)
    {
        this.volume = volume;
        if (this.playing)
            this.gainNode.gain.setValueAtTime(volume, this.ctx.currentTime);
        if (volume == 0)
            this.source_element.parent().find(".zzmplay-mute-button").html("🔇");
        else
            this.source_element.parent().find(".zzmplay-mute-button").html("🔊");
    }

    set_playback_time(now)
    {
        let s = Date.now() - this.playback_start_time + parseInt(this.start_offset_ms);
        this.source_element.parent().find(".progress").html(this.format_time(Math.floor(s / 1000)));
        this.source_element.parent().find(".zzmplay-seek").val(s);
    }

    seek(ms)
    {
        if (this.playing)
            this.stop();
        this.start_offset_ms = ms;
        this.source_element.parent().find(".progress").html(this.format_time(ms / 1000));
    }

    toggle_prefix_required(value)
    {
        this.prefix_required = value;
    }

    update_composition_url()
    {
        let base = $("input[name=url]").data("base");
        let notes = encodeURIComponent(this.play_commands);
        let full = base + notes.replaceAll("\n", "&play="); //+ "&prefix=" + (this.prefix_required ? 1 : 0);
        full = full.slice(0, 2000);
        $("input[name=url]").val(full);
        $("#zzm-comp-length").html(full.length);
    }
}

function update_playback_time(idx)
{
    ZZM_WIDGETS[idx].set_playback_time();
}

$(document).ready(function (){
    $(".zzmplay-widget").each(function (){
        let raw = $(this).find(".zzmplay-raw").val();
        let widget = $(this);
        let source_element = $(this).find(".zzmplay-raw");
        let mutable = $(this).data("mutable") ? true : false;
        let museum_zzm_audio_player = new Museum_ZZM_Audio_Player(raw, source_element, mutable, widget);
        ZZM_WIDGETS.push(museum_zzm_audio_player);
        let idx = ZZM_WIDGETS.length - 1;
        ZZM_WIDGETS[idx].widget_idx = idx;
        $(this).data("zzm-idx", idx);
    });

    $(".zzmplay-play-button").click(function (){
        let idx = $(this).parent().data("zzm-idx");
        ZZM_WIDGETS[idx].play_pause($(this));
    });

    $(".zzmplay-mute-button").click(function (){
        let idx = $(this).parent().data("zzm-idx");
        ZZM_WIDGETS[idx].toggle_mute();
    });

    $(".zzmplay-source-button").click(function (){
        let idx = $(this).parent().parent().data("zzm-idx");
        let current = $(this).hasClass("show") ? "show" : "hide";
        $(this).toggleClass("show", "hide");
        ZZM_WIDGETS[idx].toggle_source(current);
    });

    $(".zzmplay-volume").on("input", function (){
        let idx = $(this).parent().data("zzm-idx");
        ZZM_WIDGETS[idx].set_volume($(this).val());
    });

    $(".zzmplay-seek").on("input", function (){
        let idx = $(this).parent().parent().data("zzm-idx");
        ZZM_WIDGETS[idx].seek($(this).val());
    });

    $("input[name=require-prefix]").on("change", function (){
        let idx = $(this).parent().parent().data("zzm-idx");
        ZZM_WIDGETS[idx].toggle_prefix_required($(this).is(":checked"));
    });
});
