"use strict";

$(document).ready(function (){
    $("#collection-add-button").click(add_item);
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

    $.ajax(
        {
            type: "POST",
            url: "/ajax/collection/add-to-collection/",
            data: form_data,
        }
    ).done(
        function (){
            console.log("It worked!");
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
