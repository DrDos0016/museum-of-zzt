"use strict"
// Debug script for all Museum pages //

$("#debug-res").text($(window).width() + "x" + $(window).height());
$("#debug-view").text($("body").width() + "x" + $("body").height());

$("#showdebug").click(function (){
    $(".debug").toggle();
    if ($("#showdebug").text() == "HIDE DEBUGGING INFORMATION")
        $("#showdebug").text("SHOW DEBUGGING INFORMATION");
    else
        $("#showdebug").text("HIDE DEBUGGING INFORMATION");
});

$("meta").each(function (){
    let key = $(this).attr("name");
    if (! key)
        key = $(this).attr("property");
    else if (key.indexOf("twitter") == 0)
        key = "t:" + key.split(":")[1];

    let val = $(this).attr("content");
    let row;

    if (key == "og:image")
        row = `<tr><th>${key}</th><td class="l">${val}</td><td rowspan="9" id="embed-preview"><img src="${val}" loading="lazy"></td></tr>`;
    else
        row = `<tr><th>${key}</th><td class="l">${val}</td></tr>`;
    $("#meta-tags").html($("#meta-tags").html() + row);
});

// Log loaded scripts
let all_scripts = document.getElementsByTagName("script");
for (let idx in all_scripts)
{
    let script = all_scripts[idx];
    if (script.attributes && script.attributes["src"])
        $("#debug-scripts-start td").append(`${script.attributes["src"].nodeValue}<br>`);
    else
        $("#debug-scripts-start td").append(`<i>Inline Script</i><br>`);
}

// Log loaded stylesheets
let all_styles = document.getElementsByTagName("link");
for (let idx in all_styles)
{
    let style = all_styles[idx];
    if (style.attributes && (style.attributes["rel"].nodeValue == "stylesheet"))
    {
        $("#debug-stylesheets-start td").append(`${style.attributes["href"].nodeValue}<br>`);
    }
}

// Inline
all_styles = document.getElementsByTagName("style");
$("#debug-stylesheets-start td").append(`<i>Inline Styles - ${all_styles.length}</i><br>`);
