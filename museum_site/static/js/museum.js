"use strict";

$(document).ready(function (){
    // Screenshot Zoom
    $(".file-screen").click(function (){
        if ($(this).css("max-width") != "100%")
            $(this).css({"max-width":"100%", "cursor":"zoom-out"});
        else
            $(this).css({"max-width":"240px", "cursor":"zoom-in"});
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

            for (idx in params)
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
        $(".content-warning").hide();
    });

    $("span[name=cw-hide-all]").click(function (){
        $(".content-warning").hide();
        var now = new Date();
        var time = now.getTime();
        var expireTime = time + (1000 * 31536000); // 1yr
        now.setTime(expireTime);
        document.cookie = "hide_content_warnings=1;expires=" + now.toGMTString() + ";path=/";
    });
});
