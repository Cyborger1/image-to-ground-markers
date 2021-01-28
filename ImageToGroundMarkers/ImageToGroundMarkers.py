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
    return ctypes.c_long(val).value, alpha

def image_to_ground_markers(imagePath, coordsTuple, minAlpha=1):
    if not(len(coordsTuple) == 3 or len(coordsTuple) == 4):
        raise ValueError('coordsTuple has to be format (wpX, wpY, plane) or (regionId, rX, rY, plane).')

    startX, startY, startPlane = region_to_wp(*coordsTuple) if len(coordsTuple) == 4 else coordsTuple

    imageFile = Image.open(imagePath, 'r')

    colorFunctions = {
        'RGB': rgba_to_int,
        'RGBA': rgba_to_int
    }

    imageMode = imageFile.mode
    if imageMode not in colorFunctions:
        raise IOError('Image format {} is not supported.'.format(imageMode))

    colorFunc = colorFunctions[imageMode]
    imageX, imageY = imageFile.size
    imageArray = imageFile.load()

    exportValues = []

    for x in range(imageX):
        for y in range (imageY):
            color, alpha = colorFunc(*imageArray[x, imageY - y - 1])
            if alpha >= minAlpha:
                rId, rX, rY, plane = wp_to_region(startX + x, startY + y, startPlane)

                valueDict = {}
                valueDict['regionId'] = rId
                valueDict['regionX'] = rX
                valueDict['regionY'] = rY
                valueDict['z'] = plane
                valueDict['color'] = colorDict = {}
                colorDict['value'] = color
                colorDict['falpha'] = 0.0

                exportValues.append(valueDict)

    return exportValues

START_WP = (2257, 5332, 0)
START_COORDS = (9043, 17, 20, 0)
IMAGE_PATH = r'rl-30x25.png'

pyperclip.copy(json.dumps(image_to_ground_markers(IMAGE_PATH, START_WP, 1)))