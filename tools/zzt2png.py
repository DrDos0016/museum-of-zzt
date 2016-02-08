# -*- coding: utf-8 -*-
from PIL import Image, ImageFont, ImageDraw
import sys, os, binascii, random

INVISIBLE_MODE  = 1 # 0: render as an empty tile | 1: render in editor style | 2: render as touched

BASE_DIR        = "/var/projects/misc/zzt2png/"
COLORS          = ["000000", "0000A8", "00A800", "00A8A8", "A80000", "A800A8", "A85400", "A8A8A8", "545454", "5454FC", "54FC54", "54FCFC", "FC5454", "FC54FC", "FCFC54", "FCFCFC"]
CHARACTERS      = [32, 32, 63, 32, 2, 132, 157, 4, 12, 10, 232, 240, 250, 11, 127, 47, 47, 47, 248, 176, 176, 219, 178, 177, 254, 18, 29, 178, 32, 206, 62, 249, 42, 205, 153, 5, 2, 42, 94, 24, 16, 234, 227, 186, 233, 79, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63]
LINE_CHARACTERS = {"0000":249, "0001":181, "0010":198, "0011":205, "0100":210, "0101":187, "0110":201, "0111":203, "1000":208, "1001":188, "1010":200, "1011":202, "1100":186, "1101":185, "1110":204, "1111":206}
GRAPHICS        = {"000000":Image.open(BASE_DIR+"gfx/black.png"), "0000A8":Image.open(BASE_DIR+"gfx/darkblue.png"), "00A800":Image.open(BASE_DIR+"gfx/darkgreen.png"), "00A8A8":Image.open(BASE_DIR+"gfx/darkcyan.png"), "A80000":Image.open(BASE_DIR+"gfx/darkred.png"), "A800A8":Image.open(BASE_DIR+"gfx/darkpurple.png"), "A85400":Image.open(BASE_DIR+"gfx/darkyellow.png"), "A8A8A8":Image.open(BASE_DIR+"gfx/gray.png"), "545454":Image.open(BASE_DIR+"gfx/darkgray.png"), "5454FC":Image.open(BASE_DIR+"gfx/blue.png"), "54FC54":Image.open(BASE_DIR+"gfx/green.png"), "54FCFC":Image.open(BASE_DIR+"gfx/cyan.png"), "FC5454":Image.open(BASE_DIR+"gfx/red.png"), "FC54FC":Image.open(BASE_DIR+"gfx/purple.png"), "FCFC54":Image.open(BASE_DIR+"gfx/yellow.png"), "FCFCFC":Image.open(BASE_DIR+"gfx/white.png")}

def open_binary(path):
    flags = os.O_RDONLY
    if hasattr(os, 'O_BINARY'):
        flags = flags | os.O_BINARY
    return os.open(path, flags)

def read(file):
    """Read one byte as an int"""
    try:
        temp = ord(os.read(file, 1))
        return temp
    except:
        return 0

def read2(file):
    """Read 2 bytes and convert to an integer"""
    try:
        part1 = binascii.hexlify(str(os.read(file, 1)))
        part2 = binascii.hexlify(str(os.read(file, 1)))
        return int(part2 + part1, 16)
    except ValueError:
        return 0

def sread(file, num):
    """Read a string of chracters"""
    array = []
    temp = ""
    for x in range(0,num):
        array.append(binascii.hexlify(str(os.read(file, 1))))
    for x in range(0,num):
        try:
            temp += chr(int(array[x], 16))
        except ValueError:
            temp += "X"
    return temp

def get_char(char, source, bg="000000"):
    ch_x = char % 16;
    ch_y = int(char / 16);
    tile = Image.new("RGBA", (8,14), color="#"+bg)
    temp = source.crop((ch_x*8,ch_y*14,ch_x*8+8,ch_y*14+14))
    
    tile = Image.alpha_composite(tile, temp)
    return tile

def render(board, stat_data, render_num):
    x,y = (0,0)
    
    canvas = Image.new("RGBA", (480,350))
    
    line_walls = {} # I am still not happy with this solution
    line_colors = {}
    
    for tiles in board:
        char        = None
        quantity    = tiles[0]
        element     = tiles[1]
        color       = tiles[2]
        
        bg = COLORS[int(color / 16)];
        fg = COLORS[color % 16];
        source = GRAPHICS[fg]
        
        for q in xrange(0,quantity):
        
            if element == 0: # Empties
                source = GRAPHICS["000000"]
                bg = COLORS[0]
                char = get_char(color, source, bg)
            elif element >= 47 and element <= 69: # Text
                source = GRAPHICS["FCFCFC"]
                if (element != 53):
                    char = get_char(color, source, COLORS[int(((element-46)*16 + 15)/16)])
                else: # White Text
                    char = get_char(color, source, COLORS[0])
            elif element == 28 and INVISIBLE_MODE != 0: # Invisible walls
                if INVISIBLE_MODE == 1:
                    char = get_char(176, source, bg)
                else:
                    char = get_char(219, source, bg)
            elif element == 36: # Object
                for stat in stat_data:
                    if stat["x"] - 1 == x/8 and stat["y"] - 1 == y/14:
                        char = get_char(stat["param1"], source, bg)
                        break
                if not char:
                    char = get_char(CHARACTERS[element], source, bg)
            elif element == 40: # Pusher
                pusher_char = 16
                for stat in stat_data:
                    if stat["x"] - 1 == x/8 and stat["y"] - 1 == y/14:
                        if (stat["y-step"] > 32767):
                            pusher_char = 30
                        elif (stat["y-step"] > 0):
                            pusher_char = 31
                        elif (stat["x-step"] > 32767):
                            pusher_char = 17
                        break
                char = get_char(pusher_char, source, bg)
            elif element == 30: # Transporter
                transporter_char = 62
                for stat in stat_data:
                    if stat["x"] - 1 == x/8 and stat["y"] - 1 == y/14:
                        if (stat["y-step"] > 32767):
                            transporter_char = 94
                        elif (stat["y-step"] > 0):
                            transporter_char = 118
                        elif (stat["x-step"] > 32767):
                            transporter_char = 60
                        break
                char = get_char(transporter_char, source, bg)
            elif element == 31: # Line Walls
                line_walls[((y/14)*60)+(x/8)] = 1;
                line_colors[((y/14)*60)+(x/8)] = color;
                char = get_char(32, source, bg)
            elif element == 4 and render_num == 0: # On the title screen, replace the player with a monitor
                if stat_data[0]["x"] - 1 == x/8 and stat_data[0]["y"] - 1 == y/14:
                    char = get_char(32, GRAPHICS["000000"], COLORS[0])
            else:
                char = get_char(CHARACTERS[element], source, bg)
            
            canvas.paste(char, (x,y))
            x += 8
            if x >= 480:
                x = 0
                y += 14
    
    # Render line walls
    line_tiles = line_walls.keys()
    for line_idx in xrange(0,1500):
        line_key = ""
        if (line_idx < 60):
            line_key += "1"
        else:
            line_key += ("1" if line_walls.get(line_idx-60) != None else "0")
        
        if (line_idx > 1440):
            line_key += "1"
        else:
            line_key += ("1" if line_walls.get(line_idx+60) != None else "0")
            
        if (line_idx % 60 == 59):
            line_key += "1"
        else:
            line_key += ("1" if line_walls.get(line_idx+1) != None else "0")
            
        if (line_idx % 60 == 0):
            line_key += "1"
        else:
            line_key += ("1" if line_walls.get(line_idx-1) != None else "0")
        
        if (line_walls.get(line_idx)):
            bg = COLORS[int(line_colors[line_idx] / 16)];
            fg = COLORS[line_colors[line_idx] % 16];
            source = GRAPHICS[fg]
            char = get_char(LINE_CHARACTERS[line_key], source, bg)
            tile_x = (line_idx % 60)
            tile_y = (line_idx / 60)
            canvas.paste(char, (tile_x*8,tile_y*14))
  
    return canvas

def main():
    if len(sys.argv) == 1:
        print "Enter ZZT (or sav) file to process"        
        file_name = raw_input("Choice: ")
        print "Enter board number to export."
        print " - Board numbers start at 0 (the title screen)"
        print " - Enter ? for a random board"
        print " - Enter A for all boards"
        render_num = raw_input("Choice: ")
        print "Enter filename for output"
        print " - Do not include the .png extension"
        print " - If exporting all boards, the files will be suffixed with a two-digit board number"
        output = raw_input("Choice: ")
    else:
        file_name = sys.argv[1]
        render_num = sys.argv[2]
        output = sys.argv[3]
    
    file = open_binary(file_name)
    
    read2(file)                                     # ZZT Bytes - Not needed
    board_count = read2(file)                       # Boards in file (0 means just a title screen)
    board_offset = 512
    
    if render_num == "?":
        render_num = random.randint(0,board_count)
    if render_num != "?" and render_num != "A":
        render_num = int(render_num)

    boards = []
    names = []
    
    
    # Parse Board
    for idx in xrange(0, board_count+1):
        os.lseek(file, board_offset, 0)             # Jump to board data
        board_size = read2(file)
        board_name_length = read(file)
        board_name = sread(file, 50)[:board_name_length]
        names.append(board_name)
        
        parsed_tiles = 0;
        board = []
        while (parsed_tiles < 1500):
            quantity = read(file);
            element_id = read(file);
            color = read(file);
            board.append([quantity, element_id, color])
            parsed_tiles += quantity;
        
        boards.append(board)
        
        # Parse Stats
        os.lseek(file, 86, 1) # Skip 86 bytes of board + message info that we don't care about
        stat_count = read2(file)
        parsed_stats = 0;
        stat_data = []
        
        while parsed_stats <= stat_count:
            stat = {}

            stat["x"] = read(file)
            stat["y"] = read(file)
            stat["x-step"] = read2(file)
            stat["y-step"] = read2(file)
            os.lseek(file, 2, 1)
            stat["param1"] = read(file)
            stat["param2"] = read(file)
            stat["param3"] = read(file)
            os.lseek(file, 12, 1)
            oop_length = read2(file)
            os.lseek(file, 8, 1)
            
            if oop_length > 32767: # Pre-bound element
                oop_length = 0;
                
            if oop_length:
                sread(file, oop_length)
            
            stat_data.append(stat)
            parsed_stats += 1
        
        if idx == render_num:
            canvas = render(boards[idx], stat_data, idx)
            canvas.save(output+".png")
            print names[idx]
            break
        
        if render_num == "A":
            canvas = render(boards[idx], stat_data, idx)
            canvas.save(output+"-"+("0"+str(idx))[-2:]+".png")
            print names[idx]
            
        board_offset += board_size + 2
if __name__ == "__main__":main()