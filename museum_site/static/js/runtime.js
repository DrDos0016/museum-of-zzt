function start()
{
    console.log("Starting runtime...");
    setInterval(update, 100);
}

function update()
{
    board = world.boards[board_number];
    console.log(board);
    console.log("Board is... " + board_number);
    console.log("Lenth", world.boards.length);

    for (var stat_idx = 0; stat_idx < board.stats.length; stat_idx++)
    {
        var stat = board.stats[stat_idx];
        var element_idx = (stat.x - 1) + ((stat.y - 1) * 60);
        var element = board.elements[element_idx];
        console.log(element_idx);
        console.log("Proccing", element.name);

        if (element.name == "Player")
        {
            move(stat_idx, stat.x + 1, stat.y);
        }
    }

    // Redraw
    renderer.render(board);
}

function move(stat_idx, x_step, y_step)
{
    var stat = board.stats[stat_idx];
    var element_idx = (stat.x - 1) + ((stat.y - 1) * 60);
    var element = board.elements[element_idx];
    var dest_element = board.elements[(dest_x - 1) + ((dest_y - 1) * 60)];

    // Update stat


    // Update element
}
