import ctypes
from PIL import Image
import json
import pyperclip

def region_to_wp(regionId, regionX, regionY, plane):
    return ((regionId >> 8) << 6) + regionX, ((regionId & 0xff) << 6) + regionY, plane

def wp_to_region(wpX, wpY, plane):
    return ((wpX >> 6) << 8) + (wpY >> 6), wpX % 64, wpY % 64, plane

def rgba_to_int(tuple):
    sz = len(tuple)
    if not(sz == 3 or sz == 4):
        return 0

    transparent = False
    val = ((tuple[0] & 0xff) << 16) + ((tuple[1] & 0xff) << 8) + (tuple[2] & 0xff)
    if sz == 4:
        val += ((tuple[3] & 0xff) << 24)
        if tuple[3] == 0:
            transparent = True
    else:
        val += 0xff << 24

    return ctypes.c_long(val).value, transparent

START_WP = [2257, 5332, 0]
IMAGE = r'D:\cybor\Pictures\importmarkers\rl.png'

imageFile = Image.open(IMAGE, 'r')
imageSize = imageFile.size
imageArray = imageFile.load()

exportValues = []

for x in range(imageSize[0]):
    for y in range (imageSize[1]):
        wpX = START_WP[0] + x
        wpY = START_WP[1] + y
        plane = START_WP[2]
        color, transparent = rgba_to_int(imageArray[x,imageSize[1] - y - 1])
        
        if not(transparent):
            regionInfo = wp_to_region(wpX, wpY, plane)

            valueDict = {}
            valueDict["regionId"] = regionInfo[0]
            valueDict['regionX'] = regionInfo[1]
            valueDict['regionY'] = regionInfo[2]
            valueDict['z'] = regionInfo[3]
            valueDict['color'] = colorDict = {}
            colorDict['value'] = color
            colorDict['falpha'] = 0.0

            exportValues.append(valueDict)

outputJSON = json.dumps(exportValues)

pyperclip.copy(outputJSON)
