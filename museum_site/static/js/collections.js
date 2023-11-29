$(document).ready(function (){
    $("#id_title").change(update_url);
    update_url();
    console.log("okay then?");
});

function update_url()
{
    var raw = $("#id_title").val();
    var formatted = raw.trim().replace(/ /g, "-").replace(/[^0-9a-zA-Z_-]/gi, "").toLowerCase();
    $("#collection-url-preview").text(formatted);
}
