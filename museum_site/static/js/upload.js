"use strict";
var zip = null;

$(document).ready(function (){
    // Submit button
    $("#submit_upload").click(function (e){
        e.preventDefault();
        $(".tag-input").each(function (){
            $(this).val($(this).val() + ",");
            $(this).trigger("input");
        });
        document.getElementById("upload_form").submit();
    });

    // Toggle "Hosted text" visibility based on Category
    $("#id_kind").change(function (){
        if ($("#id_kind").val() != "itch")
            $(".field-wrapper[data-field='hosted_text']").show();
        else
        {
            $(".field-wrapper[data-field='hosted_text']").hide();
            $("#id_hosted_text").val("");
        }
    });
    $("#id_kind").change() // Call event on page load
});


function parse_zip_file(file)
{
    zip = new JSZip();
    console.log("Parsing Zip File...");
    zip.loadAsync(file).then(function(zip){
        var hr_size = filesize_format(file.size);

        $(".upload-info").html(
        `<div class="file-list-header">
            <span class="file-name">${file.name}</span>
            <span class="file-size">${hr_size}</span>
        </div>
        <ul class="file-list">
        </ul>
        `);

        // Generate options for preview images
        $("#id_generate_preview_image > option").each(function (){
            if ($(this).val() != "AUTO" && $(this).val() != "NONE")
                $(this).remove();
        });
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
