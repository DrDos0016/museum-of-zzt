# coding=utf-8
from __future__ import unicode_literals
import codecs

chars = list(" ☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼ !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ ")

x = 0
y = 0
num = 0

fh = codecs.open("x.html", encoding='utf-8', mode='w')
text = ""

for c in chars[:64]:
    text += "<tr>\n"
    text += "    <td>"+("00"+str(num))[-3:]+"</td>\n"
    text += "    <td>"+(chars[num])+"</td>\n"
    text += "    <td><div class=\"char\" style=\"background-position:"+str(x)+"px "+str(y)+"px\"></div></td>\n"
    
    text += "    <td>"+("00"+str(num+64))[-3:]+"</td>\n"
    text += "    <td>"+(chars[num+64])+"</td>\n"
    text += "    <td><div class=\"char\" style=\"background-position:"+str(x)+"px "+str(y-56)+"px\"></div></td>\n"
    
    text += "    <td>"+("00"+str(num+128))[-3:]+"</td>\n"
    text += "    <td>"+str(num+128)+"</td>\n"
    text += "    <td><div class=\"char\" style=\"background-position:"+str(x)+"px "+str(y-112)+"px\"></div></td>\n"
    
    text += "    <td>"+("00"+str(num+192))[-3:]+"</td>\n"
    text += "    <td>"+(chars[num+192])+"</td>\n"
    text += "    <td><div class=\"char\" style=\"background-position:"+str(x)+"px "+str(y-168)+"px\"></div></td>\n"
    
    text += "</tr>\n"
    
    num += 1
    x -= 8
    if abs(x) >= 128:
        x = 0
        y -= 14
    
fh.write(text)
fh.close()