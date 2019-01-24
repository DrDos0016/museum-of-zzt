import zookeeper

YOUTUBE_DESC = """Livestream of the ZZT world "{title}" by {author} ({year})



Download: https://museumofzzt.com/file/{letter}/{filename}
Play online: https://museumofzzt.com/play/{letter}/{filename}

Watch other live ZZT streams - https://twitch.tv/worldsofzzt
====================

Follow Worlds of ZZT on Twitter - https://twitter.com/worldsofzzt
Check out the Museum of ZZT - https://museumofzzt.com
Support Worlds of ZZT on Patreon - https://patreon.com/worldsofzzt
"""

def main():
    # 7,19 through 35,23. 29x5 workable area, x=21 is center)
    init_lines = []
    title1 = input("Line 1 (game title): ")
    init_lines.append(title1)

    title2 = input("Line 1 (game title 2): ")
    init_lines.append(title2)

    author = input("Line 3 (author): ")
    init_lines.append(author)

    company = input("Line 4 (company): ")
    init_lines.append(company)

    year = input("Line 5 (year): ")
    init_lines.append("-" + year + "-")

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

    # Text overlay
    with open("/mnt/ez/documents/wozzt/stream_text.txt", "w") as fh:
        fh.write(title1 + " " + title2 + "\n")
        fh.write("By: " + author + "\n")
        fh.write(year)

    # Youtube Description
    with open("/mnt/ez/documents/wozzt/youtube_desc.txt", "w") as fh:
        letter = input("Letter for play/view URLS: ").lower()
        filename = input("Filename play/view URLS (with extension): ")
        formatted = YOUTUBE_DESC.format(
            title=(title1 + " " + title2).strip(),
            author=author,
            year=year,
            letter=letter,
            filename=filename
        )
        fh.write(formatted)



    return True

if __name__ == "__main__":
    main()
