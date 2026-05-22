"use strict";

var CP437_TO_UNICODE = [
    0, 9786, 9787, 9829, 9830, 9827, 9824, 8226, 9688, 9675, 9689, 9794, 9792, 9834, 9835, 9788,
    9658, 9668, 8597, 8252, 182, 167, 9644, 8616, 8593, 8595, 8594, 8592, 8735, 8596, 9650, 9660,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
    48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
    64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
    80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
    96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
    112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 8962,
    199, 252, 233, 226, 228, 224, 229, 231, 234, 235, 232, 239, 238, 236, 196, 197,
    201, 230, 198, 244, 246, 242, 251, 249, 255, 214, 220, 162, 163, 165, 8359, 402,
    225, 237, 243, 250, 241, 209, 170, 186, 191, 8976, 172, 189, 188, 161, 171, 187,
    9617, 9618, 9619, 9474, 9508, 9569, 9570, 9558, 9557, 9571, 9553, 9559, 9565, 9564, 9563, 9488,
    9492, 9524, 9516, 9500, 9472, 9532, 9566, 9567, 9562, 9556, 9577, 9574, 9568, 9552, 9580, 9575,
    9576, 9572, 9573, 9561, 9560, 9554, 9555, 9579, 9578, 9496, 9484, 9608, 9604, 9612, 9616, 9600,
    945, 223, 915, 960, 931, 963, 181, 964, 934, 920, 937, 948, 8734, 966, 949, 8745,
    8801, 177, 8805, 8804, 8992, 8993, 247, 8776, 176, 8729, 183, 8730, 8319, 178, 9632, 160
];

$(document).ready(function (){
    // New Screenshot Zoom
    $(".zoomable").click(function (){
        $(this).toggleClass("thumbnail zoomed");
    });

    // Set initial zoom
    if (global_zoomed_state && (window.location.pathname != "/worlds-of-zzt/"))
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
        let resp = (on_off == "on") ? "Images expanded" : "Thumbnails restored";
        toggle_response(resp);
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
    let cur = $(this).data("expanded");
    let after = (cur == "1") ? "0": "1";
    let text = "Shower " + {"0": "All", "1": "Some"}[after];
    $(this).data("expanded", after);
    $(this).html(text);
    $(this).parent().next(".value").toggleClass("expanded");
}

function init_expandable_model_block_fields()
{
    $(".model-block-data .datum .value, .model-block-meta .datum .value").each(function (){
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

function toggle_response(resp)
{
    $("#toggle-response").html(resp);
    $("#toggle-response").fadeOut(2000, function(){
        $(this).html("");
        $(this).show();
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
        raw = raw.toLowerCase();
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
