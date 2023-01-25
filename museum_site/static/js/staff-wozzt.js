"use strict"

$(document).ready(function (){
    $("input[name=update-priority]").click(function (){
        var priority = $(this).prev("input[name=priority]").val();
        var pk = $(this).parents(".model-block").data("pk");
        update_entry_priority(pk, priority);
    });

    $("input[name=delete]").click(function (){
        var pk = $(this).parents(".model-block").data("pk");
        delete_entry(pk);
    });
});

function update_entry_priority(pk, priority)
{
    $.ajax({
        url:window.location,
        method:"POST",
        data:{
            "action":"set-priority",
            "id": pk,
            "priority": priority,
            "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
        }
    }).done(function (data){
        location.reload();
    });
}

function delete_entry(pk)
{
    $.ajax({
        url:window.location,
        method:"POST",
        data:{
            "action":"delete",
            "id": pk,
            "csrfmiddlewaretoken": $("input[name=csrfmiddlewaretoken]").val()
        }
    }).done(function (data){
        location.reload();
    });
}
