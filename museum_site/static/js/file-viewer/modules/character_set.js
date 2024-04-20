export class Character_Set
{
    constructor()
    {
        this.name = "Codepage 437";
        this.path = "/static/js/file-viewer/res/charset/cp437.png";
        this.loaded = false;
        this.image = null;
        this.tile_width = 8;
        this.tile_height = 14;
    }

    async load()
    {
        let image;
        const promise = new Promise(resolve => {
            image = new Image();
            image.onload = resolve;
            image.src = this.path;
        });

        await promise;
        console.log("Loaded charset");
        this.image = image;
        this.loaded = true;
        return true;
    }
}
