'''
Created on 4/04/2015

@author: Alex Montes Barrios
'''
import codecs
from PIL import Image, ImageTk

# import xml.etree.ElementTree as ET
# import tkMessageBox
# import json

ROMBO         = '018003c007e00ff01ff83ffc7ffeffffffff7ffe3ffc1ff80ff007e003c00180'
FLECHA_IZQ    = '0180038007800f801f803fff7fffffffffff7fff3fff1f800f80078003800180'
FLECHA_I      = '0180038007000e001c0038007000ffffffff700038001c000e00070003800180'
CFLECHA_I     = '0180038007000e001c0038007000e000e000700038001c000e00070003800180' 
CFLECHA_DOBLE = '01830387070e0e1c1c38387070e0e1c0e1c070e038701c380e1c070e03870183'
WINDOW_MAX    = '00007ffe7ffe7ffe6006600660066006600660066006600660067ffe7ffe0000' 
WINDOW_RESTORE= '00007fe07fe06060606067fe67fe666666667fe67fe60606060607fe07fe0000'
WINDOW_MIN    = '0000000000000000000000003ffc3ffc3ffc3ffc000000000000000000000000'
              
# FLECHA_DER    = '07e007e007e007e007e007e007e0ffffffff7ffe3ffc1ff80ff007e003c00180'
# FLECHA_ABAJO  = '018001c001e001f001f8fffcfffefffffffffffefffc01f801f001e001c00180'
# FLECHA_ARRIBA = '0180038007800f801f803fff7fffffffffff7fff3fff1f800f80078003800180'
CIRCULO       = '01000fe01ff03ff87ffc7ffc7ffcfffe7ffc7ffc7ffc3ff81ff00fe001000000'
ANILLO        = '01000fe01ff03ef8783c701c701ce00e701c701c783c3ef81ff00fe001000000'


dataB = [
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

datab = [
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]



def bitMapToString(bitMap):
    hNum = ''
    for j in range(len(bitMap)):
        for i in range(int(len(bitMap[0])/4)):
            hNum += "{0:x}".format(sum(elem*2**(3-k) for k, elem in enumerate(bitMap[j][4*i:4*(i+1)])))
    return hNum

def getIconImageTk(imageStr):
    imSize = int((len(4*imageStr))**0.5)
    imString = codecs.decode(imageStr,'hex')
    im = Image.frombytes('1', (imSize, imSize), imString)
    im = ImageTk.BitmapImage(im)
    return im
    

if __name__ == '__main__':
    iconString = bitMapToString(datab)
    print(iconString)
    icon = getIconImageTk(iconString)
    icon.show()
    print('program terminated')
    