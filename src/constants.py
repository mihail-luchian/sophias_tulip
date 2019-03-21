import os.path

#

R = 0
G = 1
B = 2

LIST_CHANNELS = [R,G,B]

Y = 0
X = 1

# FOLDER constants
GO_BACK = '..'
PATH_ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), GO_BACK)
FOLDER_DATA = 'data'
FOLDER_IMGS = 'imgs'
FOLDER_EXPORT = 'exports'
PATH_FOLDER_DATA = os.path.join(PATH_ROOT, FOLDER_DATA)
PATH_FOLDER_IMGS = os.path.join(PATH_FOLDER_DATA,FOLDER_IMGS)
PATH_FOLDER_EXPORTS = os.path.join(PATH_ROOT, FOLDER_EXPORT)
PATH_FOLDER_EXPORTS_NN = os.path.join(PATH_FOLDER_EXPORTS, 'nn')


# FILE
FILE_TULIP_HIGH = 'tulip_high.jpg'
FILE_TULIP_LOW = 'tulip_low.jpg'
FILE_KEUKENHOF_HIGH = 'keukenhof_high.jpg'
FILE_KEUKENHOF_LOW = 'keukenhof_low.jpg'
PATH_FILE_TULIP = os.path.join(PATH_FOLDER_IMGS, FILE_TULIP_HIGH)
PATH_FILE_TULIP_LOW = os.path.join(PATH_FOLDER_IMGS,FILE_TULIP_LOW)
PATH_FILE_KEUKENHOF = os.path.join(PATH_FOLDER_IMGS, FILE_KEUKENHOF_HIGH)
PATH_FILE_KEUKENHOF_LOW = os.path.join(PATH_FOLDER_IMGS,FILE_KEUKENHOF_LOW)


