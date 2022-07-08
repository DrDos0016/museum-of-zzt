"use strict";

$(document).ready(function (){
    $("#collection-add-button").click(add_item);
    $("#collection-remove-button").click(remove_item);
    $("#collection-arrange-button").click(arrange_collection);
    $("input[name=field_filter]").val("");
    $("input[name=field_filter]").keyup(function (){
        filter_file_list($(this).val(), $(this).data("target"));
    });
    $("select[name=entry_id]").change(load_entry);
    $("#edit-entry-button").click(update_collection_entry);

    $("button[name=field_filter_clear_button]").click(function (){
        var target = $(this).data("target");
        var field = $(this).data("field");
        $(field).val("");
        filter_file_list("", target);
    });

    $("input[name=associated_file]").click(function (){
        $("#added-item-text").html("");
        $("#id_associated_file li.selected").removeClass("selected");
        $(this).parent().parent().addClass("selected")
    });

    bind_arrangeables();
});

function add_item()
{
    var form_data = {
        "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
        "zfile_id": $("input[name=associated_file]:checked").val(),
        "collection_description": $("textarea[name=collection_description]").val(),
        "collection_id": $("input[name=collection_id]").val(),
    }

    // Blank the fields
    var original_text = $("#collection-add-button").val();
    var item_name = $("input[name=associated_file]:checked").parent().text().trim();
    $("#collection-add-button").prop("disabled", true);
    $("#id_associated_file li.selected").removeClass("selected");
    $("#collection-add-button").val("Wait...");
    $("input[name=associated_file]:checked").prop("checked", false);
    $("textarea[name=collection_description]").val("");

    $.ajax(
        {
            type: "POST",
            url: "/ajax/collection/add-to-collection/",
            data: form_data,
        }
    ).always(
        function (e){
            console.log("E", e);
            if (e == "SUCCESS")
            {
                $("#added-item-text").html("Added " + item_name);
                get_collection_contents();

            }
            else
            {
                $("#added-item-text").html(e);
            }
            $("#collection-add-button").val(original_text);
            $("#collection-add-button").prop("disabled", false);
        }
    );
}

function remove_item()
{
    var form_data = {
        "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
        "zfile_id": $("input[name=removed_file]:checked").val(),
        "collection_id": $("input[name=collection_id]").val(),
    }

    // Blank the fields
    var original_text = $("#collection-remove-button").val();
    var item_name = $("input[name=removed_file]:checked").parent().text().trim();
    $("#collection-remove-button").prop("disabled", true);
    $("#id_removed_file li.selected").removeClass("selected");
    $("#collection-remove-button").val("Wait...");

        $.ajax(
        {
            type: "POST",
            url: "/ajax/collection/remove-from-collection/",
            data: form_data,
        }
    ).always(
        function (e){
            if (e == "SUCCESS")
            {
                $("#removed-item-text").html("Removed " + item_name);
                $("input[name=removed_file]:checked").parent().parent().remove();
                $("#collection-remove-button").prop("disabled", false);
                $("#collection-remove-button").val(original_text);
                $(".model-block[data-pk="+form_data["zfile_id"]+"]").next().remove();
                $(".model-block[data-pk="+form_data["zfile_id"]+"]").remove();
            }
            else
            {
                $("#removed-item-text").html(e);
            }
        }
    );
}

function get_collection_contents()
{
    $.ajax(
        {
            type: "GET",
            url: "/ajax/collection/get-collection-addition/",
            data: {
                "collection_id": collection_id
            },
        }
    ).always(
        function (){
            $("#collection-contents").append(resp);
        }
    );
}

function filter_file_list(filter, target)
{
    console.log("Hewwo?", filter, target);
    if (filter || ! target)
        return false;
    //var filter = $("input[name=field_filter]").val();
    $(target).each(function (){
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

function bind_arrangeables()
{
    $(".arrangeable").unbind();

    $(".arrangeable").on("dragstart", function (e){
        const dt = e.originalEvent.dataTransfer;
        dt.effectAllowed = "move";
        dt.setData("text/html", $(this).prop("outerHTML"));
        $(this).addClass("dragging");
        console.log(dt);
    });
    $(".arrangeable").on("dragend", function (e){
        $(this).removeClass("dragging");
    });
    $(".arrangeable").on("dragover", function(e){
        e.preventDefault()
        if ($(this).hasClass("dragging") || $(this).data("has-ghost")) // Dropping onto dragged tag
            return false;
        $(this).data("has-ghost", 1);
        $(this).after("<li class='arrangeable-ghost'>...</li>");
    });
    $(".arrangeable").on("dragleave", function (e){
        $(this).data("has-ghost", 0);
        $(".arrangeable-ghost").remove();
    });
    $(".arrangeable").on("drop", function (e){
        e.preventDefault();
        e.stopPropagation();
        $(".arrangeable-ghost").remove();
        if ($(this).hasClass("dragging")) // Dropping onto dragged tag
            return false;

        // Reposition
        const data = e.originalEvent.dataTransfer.getData("text/html");
        $(".dragging").remove();
        $(this).after(data);

        // Rebind!
        bind_arrangeables();
    });
}

function arrange_collection()
{
    var order = "";
    $("input[name=arrange_file]").each(function (){
        order += $(this).val() + "/";
    });

    var form_data = {
        "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
        "order": order.slice(0, -1),
        "collection_id": $("input[name=collection_id]").val(),
    }

    // Blank the fields
    $("#collection-arrange-button").prop("disabled", true);

    $.ajax(
        {
            type: "POST",
            url: "/ajax/collection/arrange-collection/",
            data: form_data,
        }
    ).always(
        function (e){
            if (e == "SUCCESS")
                window.location.reload();
        }
    );
}

function load_entry()
{
    var pk = $("select[name=entry_id]").val()
    if (pk != "N/A")
    {
        var desc = $("#entry-" + pk).val();
        $("#edit-entry-button").prop("disabled", false);
        $("textarea[name=collection_description]").val(desc);
    }
    else
    {
        $("#edit-entry-button").prop("disabled", true);
        if ($("input[name=preview-image]").val() == pk)
            $("input[name=set-preview-image]").prop("checked", true);
        else
            $("input[name=set-preview-image]").prop("checked", false);
        return false;
    }

}

function update_collection_entry()
{
    var form_data = {
        "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val(),
        "collection_id": $("input[name=collection_id]").val(),
        "entry_id": $("select[name=entry_id]").val(),
        "desc": $("textarea[name=collection_description]").val(),
        "set_preview": $("input[name=set-preview-image]").prop("checked"),
    }

    $.ajax(
        {
            type: "POST",
            url: "/ajax/collection/update-collection-entry/",
            data: form_data,
        }
    ).always(
        function (e){
            if (e == "SUCCESS")
            {
                window.location.reload();
            }
            else
            {
                $("#edited-entry-text").html("Failed to update " + $("select[name=entry_id] option:selected").html() + "!");
            }
        }
    );
}
