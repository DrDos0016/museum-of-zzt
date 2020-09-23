"use strict";

$(document).ready(function (){
    // Screenshot Zoom
    $(".screenshot-thumb").click(function (){
        $(this).toggleClass("zoomed");
        var parent = $(this).parent();

        if (parent.hasClass("overview-block"))
        {
            parent.toggleClass("ob-zoomed");
        }
    });

    // Browse Letters Select-based Input
    $("#letter-button").click(function (){
        var letter = $("#letter-select").val().toLowerCase();
        if (letter)
            window.location = "/browse/"+letter;
    });

    // Reload on sort change
    $(".pages select[name=sort]").change(function (){
        var location = ("" + window.location);

        if (location.indexOf("?") == -1)
            window.location = "?sort="+$(this).val();
        else
        {
            var qs = location.split("?")[1];
            var params = qs.split("&");
            var new_qs = "?";
            console.log(qs);
            console.log(params);

            for (var idx in params)
            {
                var key = params[idx].split("=")[0];
                var val = params[idx].split("=")[1];

                if (key == "sort")
                    new_qs += key + "=" + $(this).val();
                else
                    new_qs += key + "=" + val;
                new_qs += "&";
            }
            new_qs = new_qs.slice(0, -1);

            // Make sure there's a sort param
            if (new_qs.indexOf("sort=") == -1)
                new_qs += "&sort="+$(this).val();

            window.location = new_qs;
        }
    });

    // Content warnings
    if (document.cookie.replace(/(?:(?:^|.*;\s*)hide_content_warnings\s*\=\s*([^;]*).*$)|^.*$/, "$1") == 1)
    {
        console.log("Hiding CWs");
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

    // Expand/Contract Middle Column
    $("#expand-contract").click(function (){
        $(this).toggleClass("expanded", "contracted");
        if ($(this).hasClass("expanded")) // Expand
        {
            console.log("EXPANDING")
            $(this).html("→ ←");
            $(".sidebar, #top-links, #logo-area").hide();
            $("body").removeClass("grid-root");
        }
        else // Contract
        {
            $(this).html("← →");
            $(".sidebar, #top-links, #logo-area").show();
            $("body").addClass("grid-root");
        }
    });

    // File association selection
    $("#alt-file-listing").change(function (){
        window.location = "?alt_file=" + $(this).val();
    });

    $("code.zzt-oop").each(function (){
        var raw = $(this).text();
        var processed = syntax_highlight(raw);
        $(this).html(processed);
    })

});

// ZZT-OOP Syntax highlighting
function syntax_highlight(oop)
{
    console.log("Running syntax highlight");
    console.log(oop);
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
