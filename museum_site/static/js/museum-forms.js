$(document).ready(function (){
    $(".widget input[type=checkbox]").click(function (){
        if ($(this).prop("checked"))
        {
            $(this).parent().addClass("selected");
        }
        else
        {
            $(this).parent().removeClass("selected");
        }
        write_selected($(this).attr("name"));
    });
    $(".widget input[type=radio]").click(function (){
        $(this).parent().parent().children().removeClass("selected");
        $(this).parent().addClass("selected");
        write_selected($(this).attr("name"));
    });

    $(".char-limited-widget").each(function (){
        $(this).on("input", function (){
            var len = $(this).val().length;
            var max_chars = $(this).attr("maxlength");
            var remaining = max_chars - len;
            $(this).prev(".chars-remaining").find("span").html(remaining);
        });
    });

    $(".clear-date-widget").click(function (){
        $(this).prevAll("input[type=date]").val("");
    });

    $(".todays-date-widget").click(function (){
        var today = new Date();
        $(this).prev("input[type=date]").val(today.toISOString().slice(0,10));
    })

    $(".widget-control-button").click(function (){
        var name = $(this).data("input-name");
        if ($(this).val() == "Clear")
            $("input[name="+name+"]:checked").click();
        else if ($(this).val() == "All")
            $("input[name="+name+"]").not(":checked").click();
        else if ($(this).val() == "Default")
        {
            var default_values = $(this).data("default").split("/");
            $("input[name="+name+"]").each(function (){
                if (default_values.indexOf($(this).val()) != -1)
                {
                    if ($(this).prop("checked") == false)
                        $(this).click();
                }
                else
                {
                    if ($(this).prop("checked") == true)
                        $(this).click();
                }
            });
        }

        write_selected(name);
    });

    $(".tag-input").on("input", function (){
        var val = $(this).val();

        if (val.indexOf(",") == -1)
            return false;

        // Begin adding the tag
        $(this).val("");
        var input_name = $(this).data("input");

        var entries = val.split(",");
        for (var idx=0; idx < entries.length; idx++)
        {
            var entry = entries[idx];

            if (! entry.trim())
                continue;

            if ($(this).hasClass("editing"))
            {
                var tag = $("#"+ input_name + "-tag-list").find(".tag.selected");
                $(tag).find(".tag-text").text(entry);
                $(tag).find("input").val(entry);
                $(tag).removeClass("selected");
                $(this).removeClass("editing");
                break;
            }
            var tag = create_tag(input_name, entry);

            $("#"+ input_name + "-tag-list").append(tag);
            $("#"+ input_name + "-tag-list").find("." + input_name + "-tag-template").last().removeClass(input_name + "-tag-template");

            // Set up tag binds
            $("#"+ input_name + "-tag-list").find(".tag-remove").last().click(remove_tag);
            $("#"+ input_name + "-tag-list").find(".tag").last().on("dragstart", drag_tag_start);
            $("#"+ input_name + "-tag-list").find(".tag").last().on("dragend", drag_tag_end);
            $("#"+ input_name + "-tag-list").find(".tag").last().on("dragover", drag_tag_over);
            $("#"+ input_name + "-tag-list").find(".tag").last().on("dragleave", drag_tag_leave);
            $("#"+ input_name + "-tag-list").find(".tag").last().on("drop", drag_tag_drop);
            $("#"+ input_name + "-tag-list").find(".tag").last().on("click", drag_tag_click);
        }
    });

    // Setup
    init_filters();
    $("input:checked").parent().addClass("selected");
    // Update remaining characters
    $(".char-limited-widget").trigger("input");
    // Convert text to tags if needed
    $(".tag-input").trigger("input");
    // Update list of checked boxes
    write_selected("details");
    write_selected("nonfilterable");
});

function init_filters()
{
    $(".filterable").each(function (){
        var filter_input = $(this).find(".widget-filter");
        var filter_clear = $(this).find(".widget-clear");
        var targets = $(this).find("label");

        // Bind clear button
        filter_clear.click(function (){
            $(filter_input).val("");
            filter_input.keyup();
        });

        // Bind filtering
        filter_input.keyup(
            {
                "filter": function (){return $(filter_input).val()},
                "targets": targets
            },
            apply_filter
        );
    });
}

function apply_filter(e)
{
    var filter = e.data.filter();
    var targets = e.data.targets;

    $(targets).each(function (){
        var text = $(this).text().trim().toLowerCase();
        if (text.indexOf(filter) == - 1)
        {
            $(this).hide();
        }
        else
        {
            $(this).show();
        }
    });
}

function write_selected(name)
{
    console.log("Writing selected", name);
    // Write out a list of all ticked inputs with a given name
    var output = "";

    $("input[name="+name+"]:checked").each(function (){
        output += $(this).parent().text() + ", ";
    });

    output = output.slice(0, -2);

    // Change blank values into None
    if (output == "")
        output = "<i>None</i>";

    $(".widget-selected[data-input-name="+name+"]").html(output);
}

// Tag functions
function create_tag(name, text)
{
    // Create a tag element
    var tag = $("." + name + "-tag-template").prop("outerHTML");
    tag = tag.replace(/\[text\]/g, text);
    return tag;
}

function remove_tag(e)
{
    $(e.target).parent().remove();
}

function drag_tag_start(e)
{
    const dt = e.originalEvent.dataTransfer;
    dt.effectAllowed = "move";
    dt.setData("text/html", $(this).prop("outerHTML"));
    $(this).addClass("dragging");
}

function drag_tag_end(e)
{
    $(this).removeClass("dragging");
}

function drag_tag_over(e)
{
    // Don't activate if there's already a ghost
    if ($(".tag-ghost").length)
        return false;

    var target = $(e.target).parent();

    // Don't activate for the dragged element
    if ($(target).hasClass("dragging"))
        return false;

    // Don't activate if the target isn't a tag for the same field
    if ($(target).data("field") != $(".dragging").data("field"))
        return false;

    var ghost = "<div class='tag-ghost'>...</div>";

    $(target).after(ghost);
}

function drag_tag_leave(e)
{
    var target = $(e.target).parent();
    $(".tag-ghost").remove();
}

function drag_tag_drop(e)
{
    e.preventDefault();
    e.stopPropagation();
    var target = $(e.target).parent();

    // Don't activate if the target isn't a tag for the same field
    if ($(target).data("field") != $(".dragging").data("field"))
        return false;

    var replacement = $(".dragging").prop("outerHTML");
    $(".tag-ghost").remove();
    $(".dragging").remove();
    $(target).after(replacement);
    $(".dragging").click(remove_tag);
    $(".dragging").on("dragstart", drag_tag_start);
    $(".dragging").on("dragend", drag_tag_end);
    $(".dragging").on("dragover", drag_tag_over);
    $(".dragging").on("dragleave", drag_tag_leave);
    $(".dragging").on("drop", drag_tag_drop);
    $(".dragging").removeClass("dragging");
}

function drag_tag_click(e)
{
    var input_element = $(this).parent().parent().find(".tag-input");
    if ($(this).hasClass("selected"))
    {
        input_element.val("");
        input_element.removeClass("editing");
        $(this).removeClass("selected");
        return true;
    }
    $(".tag.selected").removeClass("selected");
    $(this).toggleClass("selected");
    input_element.addClass("editing");
    input_element.val($(this).find(".tag-text").text());
    input_element.select();
}