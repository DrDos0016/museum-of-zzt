import { Handler } from "./handler.js";

export class Image_Handler extends Handler
{
    constructor()
    {
        super();
        this.name = "Image Handler";
    }

    render(fvpk, bytes) {
        $(".envelope.active").removeClass("active");
        let envelope_id = "#envelope-" + fvpk;
        if ($(envelope_id).length == 0)
            this.create_envelope(fvpk, "image");

        console.log("ENV ID", envelope_id);
        console.log("ENV", $(envelope_id));
        let envelope = $(envelope_id);

        // Do the work
        console.log("Displaying...", fvpk);
        const img = document.createElement("img");
        img.src = "data:image/png;base64," + btoa(String.fromCharCode.apply(null, bytes));
        console.log("IMG IS", img);
        envelope.html(img);
        envelope.addClass("active");
        console.log(envelope);
    }
}
