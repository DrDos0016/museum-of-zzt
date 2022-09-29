"use strict";

var CROP_CONTROLS = `<div id='crop-controls' class="cp437">
[<div id="active"></div>]
L: <input name="top" value="">
T: <input name="left" value="">
R: <input name="bottom" value="">
B: <input name="right" value="">
(​r0p: <input id="crop-output">
<label><input id="mcrop" type="checkbox" value="mcrop" style="height:20px"> M(r0p</label>
<label><input id="szzt" type="checkbox" value="szzt" style="height:20px"> SZZT/label>
<div style="display:none">
Raw X/Y: <input name="raw-xy" value="-/-">
Tile X/Y: <input name="tile-xy" value="-/-">
</div>
</div>`;

var CHAR_WIDTH = 8;
var CHAR_HEIGHT = 14;
var H_RES = 80;
var V_RES = 25;

var click_coord = null;

$(document).ready(function (){
    console.log("Loaded debug crop tool.");

    $(".zzt-img").click(crop);
    $("body").append(CROP_CONTROLS);

    $("#crop-controls input").click(function (){$(this).select()});
    $("#crop-controls input").keyup(function (e){ adjust(e) });
    $("#crop-controls input").keyup(preview);
    $("body").keyup(function (e){ reset(e) });
    $("#szzt").click(function (){
        if ($(this).prop("checked"))
        {
            CHAR_WIDTH = 16;
            CHAR_HEIGHT = 16;
            H_RES = 40;
            V_RES = 25;
            console.log("Super ZZT Mode");
        }
        else
        {
            CHAR_WIDTH = 8;
            CHAR_HEIGHT = 14;
            H_RES = 80;
            V_RES = 25;
            console.log("ZZT Mode");
        }
    });
});


var crop = function (data){
    if ($(this).hasClass("editing"))
    {
        translate_click(data);
        return true;
    }

    // First click
    click_coord = null;
    $(".zzt-img").removeClass("editing");
    $("#mcrop").prop("checked", false);
    $("#active").html($(this).children().attr("alt"));
    $("input[name=top]").val(1);
    $("input[name=left]").val(1);
    $("input[name=bottom]").val(H_RES);
    $("input[name=right]").val(V_RES);
    $("input[name=top]").click();
    $("input[name=raw-xy]").val("0/0");
    $("input[name=tile-xy]").val("0/0");
    $(this).addClass("editing");
};


var adjust = function (e){
    if (e.key != "ArrowUp" && e.key != "ArrowDown")
        return false;

    var adjusted = parseInt($("#crop-controls input:focus").val());
    if (e.key == "ArrowUp")
        adjusted++;
    else
        adjusted--;
    $("#crop-controls input:focus").val(adjusted);
    return true;
};


var preview = function (){
    console.log("Applying...");
    var t = parseInt($("input[name=top]").val()) - 1;
    var l = parseInt($("input[name=left]").val()) - 1;
    var b = parseInt($("input[name=bottom]").val()) - 1;
    var r = parseInt($("input[name=right]").val()) - 1;

    var left = t * CHAR_WIDTH;
    var top = l * CHAR_HEIGHT;
    var w = (b - t + 1) * CHAR_WIDTH;
    var h = (r - l + 1) * CHAR_HEIGHT;

    console.log("WIDTH IS", w);
    console.log("HEIGHT IS", h);

    $(".zzt-img.editing").children().css({"max-width": "none", "position": "relative", "left": -1 * left, "top": -1 * top});
    $(".zzt-img.editing").css({"width": w, "height":h});

    var output = `tl='${t+1},${l+1}' br='${b+1},${r+1}'`;
    if ($("#mcrop").is(":checked"))
        output += " mc=1";
    $("#crop-output").val(output);

};

function translate_click(data){
    var rect = $(".editing").children()[0].getBoundingClientRect();
    var raw_x = data.pageX - rect.left - document.querySelector("html").scrollLeft - 1;
    var raw_y = data.pageY - rect.top - document.querySelector("html").scrollTop - 1; // minus 1px for the left and top border
    var tile_x = parseInt(raw_x / CHAR_WIDTH) + 1;
    var tile_y = parseInt(raw_y / CHAR_HEIGHT) + 1;
    $("input[name=raw-xy]").val(raw_x + "/" + raw_y);
    $("input[name=tile-xy]").val(tile_x + "/" + tile_y);

    if (click_coord)
    {
        $("input[name=top]").val(click_coord[0]);
        $("input[name=left]").val(click_coord[1]);
        $("input[name=bottom]").val(tile_x);
        $("input[name=right]").val(tile_y);
        preview();

    }
    else
    {
        click_coord = [tile_x, tile_y];
    }
}

function reset(e)
{
    // R to reset the current crop
    if (e.keyCode != 82)
        return false;

    click_coord = null;
    $("input[name=top]").val(1);
    $("input[name=left]").val(1);
    $("input[name=bottom]").val(H_RES);
    $("input[name=right]").val(V_RES);
    $("input[name=top]").click();
    $("input[name=raw-xy]").val("0/0");
    $("input[name=tile-xy]").val("0/0");
    preview();
}
