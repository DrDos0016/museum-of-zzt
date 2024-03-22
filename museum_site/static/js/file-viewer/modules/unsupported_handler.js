import { Handler } from "./handler.js";

export class Unsupported_Handler extends Handler
{
    constructor()
    {
        super();
        this.name = "Unsupported Handler";
        this.envelope_css_class = "unsupported";
    }

    generate_html() {
        return "<b>This file is not supported for in-browser rendering.</b>";
    }
}
