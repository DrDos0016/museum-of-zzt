export class Handler
{
    constructor() {
        this.name = "Base Handler";
        this.parsed = false;
        this.bytes_idx = 0;
        this.og_prop = "Base OG Property";
    }


    render(fvpk, bytes) {
        console.log("Base handler");
        if (! this.parsed)
            this.parse_bytes(bytes);
    }

    create_envelope(id, kind) {
        $("#fv-main").append(`<div class="envelope envelope-${kind}" id="envelope-${id}">Hello</div>`);
    }

    parse_bytes(bytes) {
        console.log("Base handler parsing bytes");
    }

    magic() {
        console.log("This is base handler magic()");
        return "FizzBuzz";
    }

    read(count) {
        return "X";
    }
}
