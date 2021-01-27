import ctypes
from PIL import Image
import json
import pyperclip

def region_to_wp(regionId, regionX, regionY, plane):
    return ((regionId >> 8) << 6) + regionX, ((regionId & 0xff) << 6) + regionY, plane

def wp_to_region(wpX, wpY, plane):
    return ((wpX >> 6) << 8) | (wpY >> 6), wpX & 0x3f, wpY & 0x3f, plane

def rgba_to_int(r, g, b, a=0xff):
    alpha = a & 0xff
    val = (alpha << 24) | ((r & 0xff) << 16) | ((g & 0xff) << 8) | (b & 0xff)
    return ctypes.c_long(val).value, alpha == 0

def image_to_ground_markers(imagePath, coordsTuple):
    if not(len(coordsTuple) == 3 or len(coordsTuple) == 4):
        raise ValueError('coordsTuple has to be format (wpX, wpY, plane) or (regionId, rX, rY, plane).')

    if len(coordsTuple) == 4:
        startWP = region_to_wp(*coordsTuple)
    else:
        startWP = coordsTuple

    imageFile = Image.open(imagePath, 'r')
    imageSize = imageFile.size
    imageArray = imageFile.load()

    exportValues = []

    for x in range(imageSize[0]):
        for y in range (imageSize[1]):
            wpX = startWP[0] + x
            wpY = startWP[1] + y
            plane = startWP[2]
            pixel = imageArray[x, imageSize[1] - y - 1]
            if len(pixel) == 3 or len(pixel) == 4:
                color, transparent = rgba_to_int(*pixel)
        
                if not(transparent):
                    regionInfo = wp_to_region(wpX, wpY, plane)

                    valueDict = {}
                    valueDict['regionId'] = regionInfo[0]
                    valueDict['regionX'] = regionInfo[1]
                    valueDict['regionY'] = regionInfo[2]
                    valueDict['z'] = regionInfo[3]
                    valueDict['color'] = colorDict = {}
                    colorDict['value'] = color
                    colorDict['falpha'] = 0.0

                    exportValues.append(valueDict)

    return json.dumps(exportValues)

START_WP = (2257, 5332, 0)
START_COORDS = (9043, 17, 20, 0)
IMAGE_PATH = r'D:\cybor\Pictures\importmarkers\rl.png'

pyperclip.copy(image_to_ground_markers(IMAGE_PATH, START_WP))