import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from properties import *
import cv2

import scipy.ndimage
import scipy.misc


##########################################################################
### SCRIPT HEADER ########################################################

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = '10.jpg'

### END OF SCRIPT HEADER #################################################
##########################################################################

image_loaded = load_tulip_low()
image_grey = cv2.cvtColor(image_loaded,code=cv2.COLOR_RGB2GRAY)

# denoising
image_blurred = scipy.ndimage.gaussian_filter(image_grey,1.5)
image_blurred = cv2.ximgproc.guidedFilter(
    image_blurred,image_blurred,radius=5,eps=1).astype('int32')


# calculating gradients
g_x = scipy.ndimage.sobel(image_blurred, axis=0)
g_y = scipy.ndimage.sobel(image_blurred, axis=1)

g = np.sqrt(g_x ** 2 + g_y ** 2).astype('float32')
theta = np.arctan2(g_x, g_y)


# non-max suppresion
theta *= 180.0 / np.pi
theta[theta > 180.0] -= 180.0

hits = np.zeros_like(g,dtype='bool')

correlate = scipy.ndimage.correlate
correlate1d = scipy.ndimage.correlate1d
convolve = scipy.ndimage.convolve
convolve1d = scipy.ndimage.convolve1d

# the east west direction
kernel = np.array([0.0, 1.0, -1.0],dtype='float32')
mask = np.logical_or(theta < 22.5, theta > 157.5)
hits[mask] = np.logical_and(correlate1d(g, kernel, axis=1)[mask] >= 0.0,
                            convolve1d(g, kernel, axis=1)[mask] >= 0.0)

# the north south direction
mask = np.logical_and(theta >= 67.5, theta < 112.5)
hits[mask] = np.logical_and(correlate1d(g, kernel, axis=0)[mask] >= 0.0,
                            convolve1d(g, kernel, axis=0)[mask] >= 0.0)

# the north-east south-west direction
kernel = np.array([[0.0, 0.0, 0.0],
                   [0.0, 1.0, 0.0],
                   [0.0, 0.0, -1.0]])
mask = np.logical_and(theta >= 22.5, theta < 67.5)
hits[mask] = np.logical_and(correlate(g, kernel)[mask] >= 0.0,
                            convolve(g, kernel)[mask] >= 0.0)

# the north-west south-east direction
kernel = np.array([[0.0, 0.0, 0.0],
                   [0.0, 1.0, 0.0],
                   [-1.0, 0.0, 0.0]])
mask = np.logical_and(theta >= 112.5, theta < 157.5)
hits[mask] = np.logical_and(correlate(g, kernel)[mask] >= 0.0,
                            convolve(g, kernel)[mask] >= 0.0)

suppressed = g.copy()
suppressed[np.logical_not(hits)] = 0.0

# final step
lower = 0.1
upper = 0.3

describe_array(suppressed,'SUPPR')
edges = suppressed.copy()
t = np.mean(edges[edges>0])*5
edges[edges > t ] = t
edges = normalize_tensor(edges)

describe_array(edges[edges>0],'EDGES')


mask_lower = edges < lower
mask_upper = edges > upper
mask_intermediate = (lower <= edges) & ( edges <= upper )
edges[mask_upper] = 1.0
edges[~mask_upper] = 0.0

kernel = np.ones((3,3))
strong_neighbours = cv2.filter2D(edges,kernel=kernel,borderType=cv2.BORDER_REFLECT,ddepth=-1)
mask_strong = strong_neighbours > 1

edges[mask_intermediate & mask_strong ] = 1.0


edges = (edges*255).astype('uint8')

if BEFORE_AFTER_COMPARISON == YES:
    image_blended = np.hstack((edges,image_grey))

export_image(EXPORT_NAME,image_blended)
print('DONE')