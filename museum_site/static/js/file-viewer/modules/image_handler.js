import { Handler } from "./handler.js";

export class Image_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Image Handler";
        this.envelope_css_class = "image";
    }

    parse_bytes() {
        this.img = document.createElement("img");
        this.img.src = "data:image/png;base64," + btoa(String.fromCharCode.apply(null, this.bytes));
    }

    generate_html() {
        return [{"target": this.envelope_id, "html": this.img}];
    }
}
