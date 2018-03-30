import constants as C
import numpy as np
from utils.file_utils import *
from properties import *
from src.scripts.sorting.sorting_utils import *

##########################################################################
### SCRIPT HEADER ########################################################


# the orientation along which the sorting takes place
ORIENTATION = X
# X : along the X orientation
# TODO implement Y case
# Y : along the Y orientation

# which pixels are affecting by the algorithm
PROCESSING_MODE = SIMPLE
# SIMPLE     : arranges pixels from darkest to brightest
# TODO implement RANDOM case
# RANDOM     : randomly reposition pixels, resulting in a cool colored grain
# TODO implement HIGHLIGHTS case
# HIGHLIGHTS : sorts the bright pixels of the image
# TODO implement SHADOWS case
# SHADOWS    : sorts the dark pixels of the image

# the size of the region that is treated as a single unit during sorting and processing
BLOCK_SIZE_X = 48
BLOCK_SIZE_Y = 48

# each block is collapsed to a feature vector of RGB
FEATURE_BLOCKS = MAX
# AVERAGE       : for each channel, the average of all the channel values is taken
# MIN           : for each channel, the min of all the channel values is taken
# MAX           : for each channel, the max of all the channel values is taken


# the feature that is associated to each pixel during sorting
FEATURE_PIXELS = AVERAGE
# CHANNEL_RED   : the red channel is taken as the basis for the comparison
# CHANNEL_GREEN : the green channel is taken as the basis for the comparison
# CHANNEL_BLUE  : the blue channel is taken as the basis for the comparison
# AVERAGE       : the average of the 3 channels is the value being sorted
# TODO implement MIN case
# MIN           : the min of the 3 channels is the value being sorted
# TODO implement MAX case
# MAX           : the max of the 3 channels is the value being sorted
# XOR           : XOR the 3 channels
# MULTIPLY      : multiply the 3 channels
# RAND_MOD_5    : sum the channels and mod reduce by a random number between 1 and 5
# TODO implement SIN case
# SIN           : the values of the channels ar passed through the sine function before being sorted

SORTING_METHOD = EACH_LINE_SMALL_TO_BIG
# EACH_LINE_SMALL_TO_BIG   : for each line sort the array from the smallest to the biggest
# EACH_LINE_BIG_TO_SMALL   : for each line sort the array from the biggest to the smallest
# TODO implement LEX_SMALL_TO_BIG
# LEX_SMALL_TO_BIG         : sort the line lexically from small to big
# TODO implement LEX_BIG_TO_SMALL
# LEX_BIG_TO_SMALL         : sort the line lexically from big to small


# Adjustable value that decides the value where the sorting ends
# THRESHOLD = 0 => no sorting
# THRESHOLD = 256 => sort everything
THRESHOLD = 180

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = '22.jpg'

### END OF SCRIPT HEADER #################################################
##########################################################################


image_loaded = load_keukenhof()
image_shape = image_loaded.shape
print(image_shape)
size_y = image_shape[0]
size_x = image_shape[1]

new_y = size_y//BLOCK_SIZE_Y
new_x = size_x//BLOCK_SIZE_X
features_block = image_loaded.reshape( (new_y,BLOCK_SIZE_Y,new_x,BLOCK_SIZE_X,3) )

features_mean = np.mean(features_block,axis=1)
features_mean = np.mean(features_mean,axis=2)
features_mean = np.mean(features_mean,axis=2)

if FEATURE_BLOCKS == AVERAGE:
    features_block = np.mean(features_block,axis=1)
    features_block = np.mean(features_block,axis=2)
elif FEATURE_BLOCKS == MIN:
    features_block = np.min(features_block,axis=1)
    features_block = np.min(features_block,axis=2)
elif FEATURE_BLOCKS == MAX:
    features_block = np.max(features_block,axis=1)
    features_block = np.max(features_block,axis=2)

print(features_block.shape)

if FEATURE_PIXELS in [CHANNEL_RED, CHANNEL_GREEN, CHANNEL_BLUE]:

    if FEATURE_PIXELS == CHANNEL_RED:
        feature_channel = C.R
    elif FEATURE_PIXELS == CHANNEL_GREEN:
        feature_channel = C.G
    elif FEATURE_PIXELS == CHANNEL_BLUE:
        feature_channel = C.B

    features_pixel = np.copy(features_block[:, :, feature_channel])

elif FEATURE_PIXELS == AVERAGE:
    features_pixel =  np.mean(features_block, axis=2)
elif FEATURE_PIXELS == XOR:
    features_pixel = np.bitwise_xor(
        features_block[:, :, C.R],
        np.bitwise_xor(features_block[:,:,C.G],features_block[:,:,C.B]))
elif FEATURE_PIXELS == MULTIPLY:
    features_pixel = (
         features_block[:, :, C.R].astype('int32')
        *features_block[:, :, C.G].astype('int32')
        *features_block[:, :, C.B].astype('int32'))
    features_pixel = np.power(features_pixel, 1 / 3)
elif FEATURE_PIXELS == RAND_MOD_5:
    features_pixel = (
         features_block[:, :, C.R].astype('int32')
        +features_block[:, :, C.G].astype('int32')
        +features_block[:, :, C.B].astype('int32'))
    rand_mods = np.random.random_integers(5,size=(new_y))
    features_pixel = features_pixel % rand_mods[:, None]


# print(features_pixel.min())
# print(features_pixel.max())

sorting_constant = 1e3
if SORTING_METHOD == EACH_LINE_SMALL_TO_BIG:
    sorting_constant *= 1
elif SORTING_METHOD == EACH_LINE_BIG_TO_SMALL:
    sorting_constant *= -1

features_pixel_thresholded = np.copy(features_pixel)
print(features_mean.shape)
print(features_pixel_thresholded.shape)
features_pixel_thresholded[features_mean >= THRESHOLD] = sorting_constant
features_sorted = np.argsort(features_pixel_thresholded, kind='mergesort')
if SORTING_METHOD == BIG_TO_SMALL:
    features_sorted = np.flip(features_sorted, axis=1)


indices = np.empty((image_shape[0],image_shape[1],2))
block_range = np.arange(BLOCK_SIZE_X)


for y in range(new_y):
    mask = np.repeat(features_mean[y] < THRESHOLD,BLOCK_SIZE_X)
    mask_inverse = np.logical_not(mask)
    if SORTING_METHOD == BIG_TO_SMALL:
        mask_pos = np.repeat(features_mean[y] >= 0,BLOCK_SIZE_X)
        mask = np.logical_and(mask_pos,mask)
    upper_limit = np.sum(mask)//BLOCK_SIZE_X
    offset = np.tile(block_range,upper_limit)

    for j in range(BLOCK_SIZE_Y):
        index_y = y*BLOCK_SIZE_Y+j
        indices_x = np.repeat(features_sorted[y, :upper_limit]*BLOCK_SIZE_X,BLOCK_SIZE_X)
        # print((indices_x+offset)[0:30])
        # print(indices.shape)
        # print(offset.shape)

        indices[index_y, mask ] = np.stack((
            np.ones(upper_limit*BLOCK_SIZE_X) * index_y,
            indices_x+offset
        )).T
        indices[index_y, mask_inverse ]= np.vstack((
            np.ones(size_x-upper_limit*BLOCK_SIZE_X)*index_y,
            np.arange(size_x)[mask_inverse]
        )).T

# print(indices[0:16,0:16])

image_sorted = shuffle_image_with_indices(image_loaded,indices)
export_image(EXPORT_NAME, image_sorted)
print('DONE')

