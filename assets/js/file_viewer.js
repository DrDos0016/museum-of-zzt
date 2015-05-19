function pull_file()
{
    $("#file_list li").removeClass("selected");
    $(this).addClass("selected");
    var valid_extensions = ["Title Screen", "hi", "txt", "doc", "jpg", "gif", "bmp", "png", "bat"];
    var filename = $(this).text();
    var split = filename.toLowerCase().split(".");
    var ext = split[split.length - 1];
    
    if (valid_extensions.indexOf(ext) == -1)
    {
        $("#details").html(filename + " is not a supported filetype that can be viewed.");
        return false;
    }
    
    $.ajax({
        url:"/ajax/get_zip_file", 
        data:{
            "letter":letter,
            "zip":zip,
            "filename":filename
        }
    }).done(function (data){
        $("#details").html(data);
    });
    
    
}

$(document).ready(function (){
    $("#file_list li").click(pull_file);
});