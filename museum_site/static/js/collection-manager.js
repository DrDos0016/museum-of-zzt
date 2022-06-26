"use strict";

$(document).ready(function (){
    $("#collection-add-button").click(add_item);
    $("input[name=field_filter]").val("");
    $("input[name=field_filter]").keyup(function (){
        filter_file_list();
    });

    $("#field_filter_clear").click(function (){
        $("input[name=field_filter]").val("");
        filter_file_list();
    });

    $("input[name=associated_file]").click(function (){
        $("#added-item-text").html("");
        $("#id_associated_file li.selected").removeClass("selected");
        $(this).parent().parent().addClass("selected")
    });
});

function add_item()
{
    var form_data = {
        "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
        "zfile_id": $("input[name=associated_file]:checked").val(),
        "collection_description": $("textarea[name=collection_description]").val(),
        "collection_id": $("input[name=collection_id]").val(),
    }
    console.log("ADDING...", form_data);

    // Blank the fields
    var original_text = $("#collection-add-button").val();
    var item_name = $("input[name=associated_file]:checked").parent().text().trim();
    $("#collection-add-button").prop("disabled", true);
    $("#id_associated_file li.selected").removeClass("selected");
    $("#collection-add-button").val("Wait...");
    $("input[name=associated_file]:checked").prop("checked", false);
    $("textarea[name=collection_description]").val();


    $.ajax(
        {
            type: "POST",
            url: "/ajax/collection/add-to-collection/",
            data: form_data,
        }
    ).done(
        function (){
            console.log("It worked!");
            $("#added-item-text").html("Added " + item_name);
        }
    ).fail(
        function (){
            console.log("It failed!");
        }
    ).always(
        function (){
            console.log("All done!");
            get_collection_contents();
            $("#collection-add-button").prop("disabled", false);
            $("#collection-add-button").val(original_text);
        }
    );
}

function get_collection_contents()
{
    console.log("CID", collection_id);
    $.ajax(
        {
            type: "GET",
            url: "/ajax/collection/get-collection-addition/",
            data: {
                "collection_id": collection_id
            },
        }
    ).done(
        function (resp){
            console.log("It worked!");
            $("#collection-contents").append(resp);
        }
    ).fail(
        function (){
            console.log("It failed!");
        }
    ).always(
        function (){
            console.log("All done!");
        }
    );
}

function filter_file_list()
{
    var filter = $("input[name=field_filter]").val();
    $("input[name=associated_file]").each(function (){
        var radio = $(this);
        var entry = $(this).parent().text().trim();

        // Uncheck and hide non-matches
        if (entry.indexOf(filter) == -1)
        {
            radio.prop("checked", "");
            $(this).parent().parent().hide();
        }
        else
        {
            $(this).parent().parent().show();
        }

    });
}
