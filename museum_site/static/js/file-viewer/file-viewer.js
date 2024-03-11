"use strict";

class File_Viewer
{
    auto_load_max_size = 2097152;  // Maximum size of a zip file to automatically parse its contents
    zip_file_path = "";
    files = {};
    default_domain = "localhost";

    add_file(filename, bytes, meta)
    {
        // Adds a file into the file registry
        this.files[filename] = {"filename": filename, "bytes": bytes, "meta": meta, "model": null};
    }

    render_file_list_item(filename)
    {
        // Writes a list litem to the page's file list section
        $("#file-list").append(`<li class="fv-content">${this.files[filename].filename}</li>`);
    }

    display_file_list()
    {
        // Writes the entire file registry to the page's file list section
        for(let [filename, file] of Object.entries(this.files))
        {
            this.render_file_list_item(filename);
        }
    }

    load_file(filename)
    {
        // Loads the
        console.log("Loading...", filename);
        fetch_file_from_zip(this.zip_file_path, filename);
    }

    parse_file(filename)
    {
        // Parses the fv file {filename}
        console.log("Parsing...", filename);
        fv.files[filename].meta["parsed"] = true;
    }

    display_file(filename)
    {
        // Displays the file {filename}
        console.log("Displaying...", filename);

        const img = document.createElement("img")
        img.src = "data:image/png;base64," + btoa(String.fromCharCode.apply(null, fv.files[filename].bytes));
        document.querySelector("#FV-DEBUG").appendChild(img);
        console.log("Ok?");
        console.log(img.src);
    }
}

let fv = new File_Viewer();
let zip = new JSZip();


$(document).ready(initialize);

function initialize()
{
    console.log("Initializing!");
    fv.default_domain = fv_default_domain;

    // Bind pre-bindables
    $("#file-load-submit").click(ingest_file);
    $("#file-list").on("click", ".fv-content", output_file);

    if (auto_load)
    {
        if (file_size < fv.auto_load_max_size)
            fetch_zip_file(auto_load);
        else
            fetch_zipinfo(auto_load);
    }
}


function fetch_zip_file(url)
{
    // Fetches the zipfile found at the provided URL. Subject to CORS so no fun remote-loading out of the box.
    console.log("Fetching url", url);
    fetch(url).then(response => response.arrayBuffer()).then(data => open_zip(data));
}

function open_zip(buffer)
{
    // Adds the contents of a zipfile into the file viewer, setting the bytes property for all files, then lists the files
    console.log("Opening zip");
    zip.loadAsync(buffer).then(function (){
        for(let [filename, file] of Object.entries(zip.files))
        {
            fv.add_file(filename, {}, {"loaded": true, "parsed": false});
            file.async("uint8array").then(data => set_file_bytes(filename, data));
        }
        fv.display_file_list();
    });
}

function set_file_bytes(filename, data)
{
    // Sets the bytes for a file in the file registry
    fv.files[filename].bytes = data;
}

function ingest_file()
{
    // Checks that a file is ready to be manually uploaded into the file registry
    if ($("input[name=file_load_widget]").val())
        ingest_file_from_upload();
}

function ingest_file_from_upload()
{
    // Adds a manually uploaded file into the file registry
    console.log("UPLOADING");
    const file = $("input[name=file_load_widget]")[0].files[0];
    var reader = new FileReader();
    reader.onload = function (e) {
        var byte_array = new Uint8Array(reader.result);
        console.log(byte_array);
        fv.add_file(file.name, byte_array, {"loaded": true, "parsed": false});
        fv.render_file_list_item(file.name);
    };
    reader.readAsArrayBuffer(file);
}

function fetch_zipinfo(url)
{
    // Fetches the zipfile's info found at the provided URL.
    fv.zip_file_path = url;
    if (url.indexOf("/") == 0)
        url = url.slice(1);
    url = "/ajax/fetch-zip-info/?path=" + url;
    console.log("Fetch zipinfo", url);
    fetch(url).then(response => response.json()).then(data => ingest_file_list_from_zipfile(data));
}

function ingest_file_list_from_zipfile(data)
{
    // Adds a zipinfo's file list into the file registry. Does not set file's bytes property.
    for (var idx = 0; idx < data["items"].length; idx++)
    {
        fv.add_file(data["items"][idx].filename, null, {"loaded": false, "parsed": false})
    }
    fv.display_file_list();
}

function fetch_file_from_zip(zipfile_path, requested_file)
{
    // Fetches a file contained in a zipfile
    if (zipfile_path.indexOf("/") == 0)
        zipfile_path = zipfile_path.slice(1);
    let url = "/ajax/fetch-zip-content/?path=" + zipfile_path + "&content=" + requested_file;
    console.log("Request -> ", url);
    fetch(url).then(response => response.arrayBuffer()).then(data => ingest_unloaded_file(data, requested_file));
}

function ingest_unloaded_file(data, requested_file)
{
    // Sets the file registry's bytes for the file to {data}. Then parses + displays it.
    console.log("Ingested unloaded file: ", requested_file);
    var byte_array = new Uint8Array(data);
    fv.files[requested_file].bytes = byte_array;
    fv.files[requested_file].meta.loaded = true;
    fv.parse_file(requested_file);
    fv.display_file(requested_file);
}


function output_file(e)
{
    // Called when clicking on a file in the registry to display. Will load/parse file as needed
    var requested_filename = e.target.textContent;
    console.log("OUTPUTTING", requested_filename);
    console.log(fv.files[requested_filename]);

    if (! fv.files[requested_filename].meta.loaded)
        fv.load_file(requested_filename)
    if (! fv.files[requested_filename].meta.parsed)
        fv.parse_file(requested_filename);

    fv.display_file(requested_filename);

}
