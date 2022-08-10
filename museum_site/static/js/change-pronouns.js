$(document).ready(function (){
    $("input[name=pronouns]").click(function (){
        custom_check($(this).val());
    });

    // Enable Custom if needed
    custom_check($("input[name=pronouns]:checked").val());
});

function custom_check(pronouns)
{
    if (pronouns == "CUSTOM")
        $("input[name=custom]").prop("disabled", false);
    else
        $("input[name=custom]").prop("disabled", true);
}
