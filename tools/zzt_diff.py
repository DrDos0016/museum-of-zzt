import os
import sys

from hashlib import md5

import zookeeper


def main():
    file1 = sys.argv[-2]
    file2 = sys.argv[-1]

    # Open the worlds
    z1 = zookeeper.Zookeeper(file1)
    z2 = zookeeper.Zookeeper(file2)

    # Compare worlds
    attrs = [
        "_total_boards", "current_board", "_world_name", "health", "ammo",
        "torches", "gems", "score", "unused", "keys"
    ]

    print(" " * 20, z1.meta.file_name.ljust(20), z2.meta.file_name)
    for attr in attrs:
        attrib_name = attr.ljust(20)
        print(attrib_name, end=" ")
        print(str(getattr(z1.world, attr)).ljust(20), end=" ")
        print(str(getattr(z2.world, attr)).ljust(20), end=" ")
        if getattr(z1.world, attr) != getattr(z2.world, attr):
            print("MISMATCH", end=" ")
            input("\nPress Enter to continue...")
        print("")

    print("=" * 78)

    # Compare board names
    print(z1.meta.file_name.ljust(40), z2.meta.file_name)
    for idx in range(0, z1.world.total_boards):
        print(z1.boards[idx].title.ljust(40), end=" ")
        print(z2.boards[idx].title.ljust(40), end=" ")
        if z1.boards[idx].title != z2.boards[idx].title:
            print("MISMATCH", end=" ")
            input("\nPress Enter to continue...")
        print("")

    print("=" * 78)

    # Compare board RLE data
    for idx in range(0, z2.world.total_boards):
        print(z1.boards[idx].title.ljust(40), end=" ")

        wip = md5()
        wip.update(str(z1.boards[idx].rle_elements).encode())
        z1_board_md5 = wip.hexdigest()

        wip = md5()
        wip.update(str(z2.boards[idx].rle_elements).encode())
        z2_board_md5 = wip.hexdigest()

        print(z1_board_md5, end=" ")
        print(z2_board_md5, end=" ")

        if z1_board_md5 != z2_board_md5:
            print("RLE ENCODING MISMATCH", end="")
            #input("\nPress Enter to continue...")
        print("")

    """
    This works, but by using addresses as soon as one board is different
    all following boards will automatically be different as well.
    # Compare board content
    attrs = [
        "size", "start_address", "element_address", "stats_address"
    ]
    for idx in range(0, z2.world.total_boards):
        print("-" * 78)
        print(z1.boards[idx].title)
        for attr in attrs:
            attrib_name = attr.ljust(20)
            print(attrib_name, end=" ")
            print(str(getattr(z1.boards[idx], attr)).ljust(20), end=" ")
            print(str(getattr(z2.boards[idx], attr)).ljust(20), end=" ")
            if getattr(z1.boards[idx], attr) != getattr(z2.boards[idx], attr):
                print("MISMATCH", end=" ")
                #input("\nPress Enter to continue...")
            print("")
    """

    return True


if __name__ == "__main__":
    main()
