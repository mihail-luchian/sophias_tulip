import os.path

INSTA_SIZE = 2000

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
FOLDER_DUMP = 'dump'
PATH_FOLDER_DATA = os.path.join(PATH_ROOT, FOLDER_DATA)
PATH_FOLDER_IMGS = os.path.join(PATH_FOLDER_DATA,FOLDER_IMGS)
PATH_FOLDER_EXPORTS = os.path.join(PATH_ROOT, FOLDER_EXPORT)
PATH_FOLDER_DUMP = os.path.join(PATH_ROOT, FOLDER_DUMP)
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

# HIERARCHICAL MARKOV MODEL CONSTANTS
TYPE_GEN = 'GENERATOR'
TYPE_PROC = 'PROCESSOR'


PATTERN_STR_INDICES = {
    '0':0,
    '1':1,
    '2':2,
    '3':3,
    '4':4,
    '5':5,
    '6':6,
    '7':7,
    '8':8,
    '9':9,

    'A':10,
    'B':11,
    'C':12,
    'D':13,
    'E':14,
    'F':15,

    'G':16,
    'H':17,
    'I':18,
    'J':19,
    'K':20,
    'L':21,
    'M':22,
}

PATTERN_INDICES_STR = {
    j : i
    for i,j in PATTERN_STR_INDICES.items()
}

DEFAULT_COLOR_STR_1 = '0/aaaaaa/1-1/aaaaaa/1-2/aaaaaa/1-3/aaaaaa/1-4/aaaaaa/1'
DEFAULT_COLOR_STR_2 =  '|'.join(
    '-'.join( str(j*5+i) + '/aaaaaa/1' for i in range(5) )
    for j in range(2)
)