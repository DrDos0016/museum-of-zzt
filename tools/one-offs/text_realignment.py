#!/usr/bin/python
import sys, codecs

def main():
    orig = open(sys.argv[1], "r").read()
    
    out = orig.replace("\n\n", "<br>")
    out = out.replace("\n", " ")
    out = out.replace("<br>", "\n")
    
    final = ""
    for line in out.split("\n"):
        #print len(line)
        if len(line) > 65:
            final += line
        else:
            final += line + "\n"
    
    file = codecs.open("aligned-"+sys.argv[1], "w", "utf-8")
    file.write(final)
    file.close()
    return True    
if __name__ == "__main__" : main()