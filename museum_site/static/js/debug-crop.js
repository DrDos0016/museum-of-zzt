"use strict";

var CROP_CONTROLS = `<div id='crop-controls'>
<div id="active"></div>
T: <input name="top" value="">
L: <input name="left" value="">
B: <input name="bottom" value="">
R: <input name="right" value="">
Crop: <input id="crop-output"></div>
</div>`;

$(document).ready(function (){
    console.log("Loaded debug crop tool.");

    $(".zzt-img").click(crop);
    $("body").append(CROP_CONTROLS);

    $("#crop-controls input").click(function (){$(this).select()});
    $("#crop-controls input").keyup(function (e){ adjust(e) });
    $("#crop-controls input").keyup(preview);
});


var crop = function (){
    $(".zzt-img").removeClass("editing");
    $(this).addClass("editing");
    $("#active").html($(this).children().attr("alt"));
    $("input[name=top]").val(1);
    $("input[name=left]").val(1);
    $("input[name=bottom]").val(80);
    $("input[name=right]").val(25);
    $("input[name=top]").click();
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
    //4,5, 15,20
    var t = parseInt($("input[name=top]").val()) - 1;
    var l = parseInt($("input[name=left]").val()) - 1;
    var b = parseInt($("input[name=bottom]").val()) - 1;
    var r = parseInt($("input[name=right]").val()) - 1;

    var left = t * 8;
    var top = l * 14;
    var w = (b - t + 1) * 8;
    var h = (r - l + 1) * 14;

    $(".zzt-img.editing").children().css({"max-width": "none", "position": "relative", "left": -1 * left, "top": -1 * top});
    $(".zzt-img.editing").css({"width": w, "height":h});

    $("#crop-output").val(`tl='${t+1},${l+1}' br='${b+1},${r+1}'`);

};
