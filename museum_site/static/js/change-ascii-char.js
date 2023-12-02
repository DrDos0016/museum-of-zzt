var ascii_idx = 0;

$(document).ready(function (){
    $("form .ascii-char-image").each(function (){
        $(this).data("idx", ascii_idx);
        ascii_idx++;
    });

    $(".ascii-char-image").click(function (){
        var num = $(this).data("idx");
        var css = $(this).attr("style");
        $("select[name=character]").val(num);
        $(".ascii-selected-number").html("#" + num);
        $(".ascii-selected-char .ascii-char-image").attr("style", css);
        update_preview();
    });

    $(".color-button").click(function (){
        let target = $(this).data("target");
        $(".color-button[data-target="+target+"]").removeClass("selected");
        $(this).addClass("selected");
        $(this).parent().find("select").val($(this).val());
        update_preview();
    });

    update_preview();
});

function update_preview()
{
    // Hastily converted from zzt_tags.py
    var CHARSET_WIDTH = 1024;
    var CHARSET_HEIGHT = 448;
    var colors = [
        "black", "darkblue", "darkgreen", "darkcyan", "darkred", "darkpurple", "darkyellow", "gray",
        "darkgray", "blue", "green", "cyan", "red", "purple", "yellow", "white"
    ];

    var scale = 3;
    var num = $("select[name=character]").val();
    var fg = $("select[name=foreground]").val();
    var bg = $("select[name=background]").val();

    var image = $("#ascii-preview-wrapper .ascii-char-image");
    image.removeClass();
    image.addClass("ascii-char-image");
    image.addClass("ega-"+bg+"-bg");

    // Adjust position by character
    var row = parseInt(num / 16);
    var col = num % 16;
    var pos_x = -8 * col;
    var pos_y = -14 * row;

    // Adjust position by foreground color
    var color = colors.indexOf(fg);
    if (color < 8)
        pos_x -= color * 128;
    else
    {
        pos_x -= (color - 8) * 128;
        pos_y -= 224;
    }

    // Adjust position by scale
    pos_x = pos_x * scale;
    pos_y = pos_y * scale;
    var size_x = CHARSET_WIDTH * scale;
    var size_y = CHARSET_HEIGHT * scale;


    image.attr(
        "style",
        "width:"+(8 * scale)+"px;height:"+(14 * scale)+"px;background-position:"+(pos_x)+"px "+(pos_y)+"px;background-size:"+(size_x)+"px "+(size_y)+"px;image-rendering: pixelated;"
    );
    return true;
}
