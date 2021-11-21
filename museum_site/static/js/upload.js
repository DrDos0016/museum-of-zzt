"use strict";
var zip = null;

$(document).ready(function (){
    // Populate SSV data if there is any on load
    repopulate_ssv("author");
    repopulate_ssv("company");
    repopulate_checkboxes("genre");
    repopulate_checkboxes("language");

    // Chars remaining
    $(".chars-remaining").each(function (){
        var field = $(this).data("field");

        $("#" + field).keyup(function (){
            var length = $(this).val().length;
            $("#" + field + "-remaining").html($("#" + field + "-remaining").data("max") - length);
        });
    });

    // Genre highlights
    $("input[name=genre]").click(function (){
        if ($(this).prop("checked"))
            $(this).parent().addClass("selected");
        else
            $(this).parent().removeClass("selected");
    });

    // Today button
    $("input[name=today]").click(function (){
        var today = new Date();
        $("#id_release_date").val(today.toISOString().slice(0,10));
    });

    // Suggestions
    $("#author-entry").bind("input", function (){
        clearTimeout($(this).data("timeout"));
        setTimeout(get_suggestions.bind(null, "#author-entry", "author"), 200);
    });

    $("#company-entry").bind("input", function (){
        clearTimeout($(this).data("timeout"));
        setTimeout(get_suggestions.bind(null, "#company-entry", "company"), 200);
    });

    // Drag and Drop Uploading
    $(".upload-area").click(function (){
        $("#id_zfile").click();
    });

    $(".upload-area").on("dragover", function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass("dragging");
    });

    $(".upload-area").on("dragleave", function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass("dragging");
    });

    $(".upload-area").on("drop", function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass("dragging");

        const dt = e.originalEvent.dataTransfer;
        const file = dt.files[0];
        $("#id_zfile")[0].files = dt.files;

        parse_zip_file(file);
    });

    $("#id_zfile").change(function (e){
        console.log("ZFILE CHANGED");
        const file = $(this)[0].files[0];
        console.log(file);
        parse_zip_file(file);
    });

    // Slash-Separated Value Fields
    $(".ssv-entry").keyup(function (){
        var val = $(this).val();
        var key = $(this).attr("id").slice(0, -6);
        // TODO THIS NEEDS TO SPLIT ON COMMA AND ADD IN BULK
        if (val.endsWith(","))
        {
            val = val.slice(0, -1);
            if (! val.trim() )  // Make sure there's data
                return false;
            add_ssv_entry(key, val);
            $(".ssv-val").unbind("click").click(function (){
                remove_ssv_entry($(this), $(this).data("key"));
            });
            update_ssv(key);
            $(this).val("");
        }
    });

    $(".ssv-entry").blur(function (){
        $(this).val($(this).val() + ",");
        $(this).keyup();
        $(this).val("");
    });

    // Select + Custom Fields
    $(".spc-select").change(function (){
        if ($(this).val() == "CUSTOM")
        {
            $(this).parent().children(".spc-custom").show();
        }
        else
        {
            $(this).parent().children(".spc-custom").hide();
        }

    });

    // Slash-Separated Checkbox Fields
    $(".ssv-checkbox").click(function (){
        var checked = $(this).prop("checked");
        var name = $(this).attr("name").slice(0, -9); // Strip "-checked"
        var ssv = "";
        $("input[name=" + name + "-checkbox]").each(function (idx){
            if ($(this).prop("checked"))
                ssv += $(this).val() + "/";
        });
        if (ssv.endsWith("/"))
            ssv = ssv.slice(0, -1);
        $("#id_" + name).val(ssv);
    });
});

function get_suggestions(selector, kind)
{
    console.log("Getting suggestions", selector, kind);
    var query = $(selector).val();
    if (! query)
        return false;

    $.ajax({
        url:"/ajax/get-"+kind+"-suggestions/",
        data:{
            "q":query,
        }
    }).done(function (data){
        var output = "";
        for (var idx in data["suggestions"])
        {
            output += '<option value="'+data["suggestions"][idx]+'">';
            console.log(idx, data["suggestions"][idx]);
        }
        $("#"+kind+"-suggestions").html(output);
        $(selector).focus();
        console.log("Suggestions to", "#"+kind+"-suggestions");
    });
};


function parse_zip_file(file)
{
    zip = new JSZip();
    console.log("Parsing Zip File...");
    zip.loadAsync(file).then(function(zip){

        var hr_size = filesize_format(file.size);

        $(".upload-info").html(
        `<div class="file-header">
            <span class="file-name">${file.name}</span>
            <span class="file-size">${hr_size}</span>
        </div>
        <ul class="file-list">
        </ul>
        `);

        for(let [filename, file] of Object.entries(zip.files)) {
            //console.log(filename, file);
            if (filename.toUpperCase().endsWith(".ZZT"))
            {
                $("#id_generate_preview_image").append(`<option value='${filename}'>${filename}</option>`);
            }
            $(".file-list").append(`<li>${filename}</li>\n`);
        }

        $(".upload-info").show();
    });

}


function update_ssv(key)
{
    $("#id_"+key).val("");
    console.log(key);
    $("#"+key+"-list .ssv-val").each(function (){
        var cur = $("#id_"+key).val();
        var entry = $(this).data("val");
        $("#id_"+key).val(cur + entry + "/");
    });
    var cur = $("#id_"+key).val().slice(0, -1);
    $("#id_"+key).val(cur);
}

function add_ssv_entry(key, val)
{
    $("#"+key+"-list").append("<div class='ssv-val' data-val='"+val+"' data-key='"+key+"'>"+val+"<span class='ssv-remove'>✖</span></div>");
}

function remove_ssv_entry(selector, key)
{
    console.log(selector);
    selector.remove();
    update_ssv(key);
}


function repopulate_checkboxes(name)
{
    // Convert previously posted SSV to other input formats
    var raw = $("#id_" + name).val();
    var list = raw.split("/");
    $("input[name=" + name + "-checkbox]").each(function (idx){
        if (list.indexOf($(this).val()) != -1)
            $(this).prop("checked", true);
    });
}


function repopulate_ssv(name)
{
    var raw = $("#id_" + name).val();
    var list = raw.split("/");
    for (var idx in list)
    {
        if (list[idx])
            add_ssv_entry(name, list[idx]);
    }
}
