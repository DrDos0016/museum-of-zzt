"use strict";

var db;
var data;
var total_size = 0;

$(document).ready(function (){
    var DBOpenRequest = window.indexedDB.open(database_name);
    DBOpenRequest.onerror = event => {
        console.log("DB Error: " + event.target.errorCode);
    }
    DBOpenRequest.onsuccess = event => {
        db = event.target.result;

        if (! db.objectStoreNames.contains("files"))
            return false;

        var transaction = db.transaction(["files"]);
        var request = transaction.objectStore("files").getAll();
        request.onsuccess = event => {
            data = request.result;
            list_files(database_name);
        }
    }

    $("input[name=allow-delete]").click(function (){
        var val = $(this).val();
        if (val == "1")
        {
            $(".db-delete-stub").hide();
            $(".db-delete-button").show();
        }
        else
        {
            $(".db-delete-button").hide();
            $(".db-delete-stub").show();
        }
    });

    $("input[name=allow-delete]").click();
});

function list_files(database_name)
{
    for (var i = 0; i < data.length; i++)
    {
        $("#save-db-table").append(
            `<tr>
                <td class="mono">${data[i].filename}</td>
                <td class="r"><span title="${data[i].value.length} bytes">${filesize_format(data[i].value.length)}</span></td>
                <td class="c"><a class="db-download-button jsLink"data-idx="${i}">Download</a></td>
                <td class="c">
                    <a class="db-delete-button jsLink" data-idx="${i}" data-size="${data[i].value.length}">Delete</a>
                    <span class="db-delete-stub">Delete</span>
                </td></tr>`
        );
        total_size += data[i].value.length;
    }

    update_total_size();
    $(".db-download-button").click(download_db_file);
    $(".db-delete-button").click(delete_db_file);
}

function download_db_file()
{
    console.log("DL DB FILE!");
    var idx = parseInt($(this).data("idx"));

    if (!data[idx])
        return false;

    if (document.getElementById("temp-dl-link"))
        document.getElementById("temp-dl-link").remove();

    var dl = document.createElement("a");
    dl.id = "temp-dl-link";
    dl.href = URL.createObjectURL(new Blob([data[idx].value], {type: "application/octet-stream" }));
    dl.download = data[idx].filename;
    dl.style.display = "none";
    document.body.appendChild(dl);
    dl.click();
}

function delete_db_file()
{
    var idx = parseInt($(this).data("idx"));

    if (!data[idx])
        return false;

    var filename = data[idx].filename;
    var transaction = db.transaction(["files"], "readwrite");
    var size = parseInt($(this).data("size"));
    $(this).parent().parent().css("visibility", "hidden");
    var request = transaction.objectStore("files").delete(filename);
    total_size -= size;
    update_total_size();
}

function update_total_size()
{
    $("#total-bytes-hr").html(filesize_format(total_size));
    $("#total-bytes-hr").attr("title", total_size + " bytes");
}
