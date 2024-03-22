import { Handler } from "./handler.js";

export class Image_Handler extends Handler
{
    constructor(fvpk)
    {
        super(fvpk);
        this.name = "Image Handler";
        this.envelope_css_class = "image";
    }

    parse_bytes(bytes) {
        this.img = document.createElement("img");
        this.img.src = "data:image/png;base64," + btoa(String.fromCharCode.apply(null, bytes));
    }

    generate_html() {
        return this.img;
    }
}
