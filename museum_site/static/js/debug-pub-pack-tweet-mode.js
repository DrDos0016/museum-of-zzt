var base = `<div id='tweet-controls'>
    <textarea id="tweet-text"></textarea>
    <div id="tweet-screens">
        <img class="tweet-image" id="ti-0">
        <img class="tweet-image" id="ti-1">
        <img class="tweet-image" id="ti-2">
        <img class="tweet-image" id="ti-3">
        <div id="tweet-copy-text">---</div>
    </div>
    <select id="tweet-files"></select>
    <input type="button" value="Next" id="tweet-next-button">
</div>`;

var idx = 0;

$(document).ready(function (){
    $("#article-meta").append(base);

    $(".model-block.detailed").each(function (){
        var pk = $(this).data("pk");
        var title = $(this).prev().text();
        $("#tweet-files").append(`<option value="${pk}">${title}</option>`);
    });

    $("#tweet-next-button").click(function (){
        console.log("IDX", idx);
        var val = $("#tweet-files option")[idx + 1].value;
        $("#tweet-files").val(val);
        prep_tweet();
    });

    $("#tweet-text").click(copy_text);
    $("#tweet-files").change(prep_tweet).change();
});

function prep_tweet()
{
    var text = "";
    var pk = $("#tweet-files").val();

    for (idx = 0; idx < $("#tweet-files option").length; idx++)
    {
        if ($("#tweet-files option")[idx].value == pk)
            break;
    }

    var obj = $(".model-block.detailed[data-pk=" + pk + "]");

    text += obj.prev().text() + "\n";

    var url = obj.find("h2.title a")[0].href;
    text += url + "\n";

    var desc = obj.next().next().text();
    text += desc + "\n";
    text = text.trim();

    $("#tweet-text").val(text);

    // Screenshots
    $("#ti-0").attr("src", "");
    $("#ti-1").attr("src", "");
    $("#ti-2").attr("src", "");
    $("#ti-3").attr("src", "");

    $("#ti-0").attr("src", obj.find(".preview-image")[0].src);

    var img_set = $($(".image-set")[idx]);

    for (var i = 0; i < img_set.find("img").length; i++)
        $("#ti-"+ (i+1)).attr("src", img_set.find("img")[i].src);
}

function copy_text()
{
    $("#tweet-text").select();
    document.execCommand("copy");
}
