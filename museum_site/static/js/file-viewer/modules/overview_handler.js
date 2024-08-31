import { Handler } from "./handler.js";

export class Overview_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Overview Handler";
        this.envelope_css_class = "overview";
        this.fv_files = {};
        this.preview_image_url = "";
        this.description = "";
        this.envelope_id = "#envelope-fvpk-overview";
        this.zip_comment = "";
    }

    parse_bytes() {
        // Overview has no bytes, but this seems like a good place to pull data from the pre-rendered HTML
        console.log("Parsing the so called bytes");
        this.preview_image_url = $("#fv-preview").attr("src");
        this.description = $("#envelope-fvpk-overview .zf-desc-wrapper").html();
        return false;
    }

    write_html() {
        console.log("Overview HTML generation");

        let targets = [
            {"target": "#zip-info", "html": this.generate_zip_info_table()},
            {"target": this.envelope_id, "html": this.generate_overview()},
        ];

        this.write_targets(targets);
        this.display_tab("zip-info");
        return true;
    }

    generate_overview()
    {
        let desc = "";
        if (this.description)
            desc = `<div class="zf-desc-wrapper"><div><p>${this.description}</p></div></div>`;
        let output = `
            <div class="zf-preview-wrapper"><img src="${this.preview_image_url}" class="image" id="fv-preview"></div>
            ${desc}
        `;
        return output;
    }

    generate_zip_info_table() {
        let output = "";
        let has_zipinfo = false;
        if (this.zip_comment)
            output += `<div>${this.zip_comment}</div>`;
        let zip_info_table = `
            <table class="zip-info-table">
            <tr><th>Filename</th><th>Mod. Date</th><th>Dir.</th><th>CRC-32</th><th>Compressed Size</th><th>Decompressed Size</th></tr>
        `;
        // TODO: CRC32 is appearing as negative?
        for(let [key, file] of Object.entries(this.fv_files))
        {
            if (file.fvpk == "fvpk-overview" || file.fvpk == "fvpk-debug")
                continue;
            let zi = file.meta.zipinfo
            if (zi)
            {
                has_zipinfo = true;
                zip_info_table += `<tr>
                    <td>${file.filename}</td>
                    <td class="c">${zi.date.toISOString().replace("T", " ").slice(0, 19)}</td>
                    <td class="c">${zi.dir ? "Y" : "N"}</td>
                    <td class="r">${zi.crc32}</td>
                    <td class="r">${zi.compressed_size}</td>
                    <td class="r">${zi.decompressed_size}</td>
                </tr>`;
            }
        }

        if (has_zipinfo)
            output += zip_info_table;
        else
            output += `<i>Zipinfo is not available for large zip files.</i>`;

        output += `</table>`;
        return output;
    }
}
