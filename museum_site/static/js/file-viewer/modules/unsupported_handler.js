import { Handler } from "./handler.js";

export class Unsupported_Handler extends Handler
{
    constructor()
    {
        super();
        this.name = "Unsupported Handler";
    }

    render(fvpk, bytes) {
        $(".envelope.active").removeClass("active");
        let envelope_id = "#envelope-" + fvpk;
        if ($(envelope_id).length == 0)
            this.create_envelope(fvpk, "image");

        let envelope = $(envelope_id);

        // Do the work
        envelope.html("Unsupported sowwy");
        envelope.addClass("active");
    }
}
