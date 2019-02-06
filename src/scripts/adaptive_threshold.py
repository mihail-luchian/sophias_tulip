import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from properties import *
import cv2


##########################################################################
### SCRIPT HEADER ########################################################

# size of region included for the threshold calculation
REGION_SIZE = 500
# the new "threshold parameter", controls the luminosity
C = 10


### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = str(C) + '.jpg'

### END OF SCRIPT HEADER #################################################
##########################################################################

image_loaded = load_keukenhof()
image_grey = cv2.cvtColor(image_loaded,code=cv2.COLOR_RGB2GRAY)


filter_size = REGION_SIZE
image_blur = cv2.boxFilter(
    image_grey,ddepth=-1,ksize=(filter_size,filter_size),borderType=cv2.BORDER_REFLECT)


image_adap_thresh = np.zeros_like(image_grey)
mask_adaptive = image_grey > (image_blur-C)
image_adap_thresh[mask_adaptive] = 255
image_adap_thresh[np.logical_not(mask_adaptive)] = 0

image_thresh = np.zeros_like(image_grey)
mask_global = image_grey > 127
image_thresh[mask_global] = 255
image_thresh[np.logical_not(mask_global)] = 0


if BEFORE_AFTER_COMPARISON == YES:
    image_blended = np.hstack((image_thresh,image_adap_thresh,image_blur,image_grey))

export_image(EXPORT_NAME,image_blended)
print('DONE')