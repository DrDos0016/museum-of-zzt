import zookeeper

def main():
    # 7,19 through 35,23. 29x5 workable area, x=21 is center)
    init_lines = []
    init_lines.append(input("Line 1 (game title): "))
    init_lines.append(input("Line 1 (game title 2): "))
    init_lines.append(input("Line 3 (author): "))
    init_lines.append(input("Line 4 (company): "))
    init_lines.append("-" + input("Line 5 (year): ") + "-")

    # Center the text
    lines = []
    for line in init_lines:
        while len(line) < 29:
            line = " " + line + " "
        lines.append(line[:29])

    print(lines)


    # Open the world
    z = zookeeper.Zookeeper("/mnt/ez/486/ZZT/projects/WoZZT.zzt")

    # Find the board
    b = None
    for board in z.boards:
        if board.title == "Stream Intro":
            b = board
            break

    # Set coordinates
    x, y = (7, 19)

    # Begin writing elements
    for line in lines:
        for character in line:
            e = board.get_element((x, y))
            # Write the element to the board
            e.id = 53
            e.character = ord(character)
            e.color_id = ord(character)
            x += 1
        x = 7
        y += 1

    # Save
    z.save()

    b.screenshot("/mnt/ez/pictures/streaming/intro")


    return True

if __name__ == "__main__":
    main()
