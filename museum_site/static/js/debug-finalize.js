"use strict";
$(document).ready(function (){
    $("article a").each(function (){
        var text = $(this).text();
        var target = $(this).attr("target");
        var path = $(this).attr("href");

        if (target == undefined)
            target = "";

        var tclass = "";
        var pclass = "";

        if (path.startsWith("http") && target != "_blank")
            tclass = "red";

        if (path.indexOf("museumofzzt.com") != -1)
            pclass = "red";

        $("#link-table").append(`<tr><td><a href="${path}" target="_blank">${text}</a></td><td class="${tclass}">${target}</td><td class="${pclass}">${path}</tr>`);
    });
});
