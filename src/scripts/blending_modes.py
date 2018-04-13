import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.image_utils import  *
from properties import *


##########################################################################
### SCRIPT HEADER ########################################################

BLEND_MODE = LIGHTER_COLOR
# a is bottom layer, b is top layer
# DARKEN        :
# MULTIPLY      : multiplies point by point one image with another
# COLOR_BURN    :
# TODO implement LINEAR_BURN blend mode
# LINEAR_BURN   :
# DARKER_COLOR  : min(aR*0.2126 + aG*0.7152 + aB*0.0722,bR*0.2126 + bG*0.7152 + bB*0.0722)
# LIGHTEN       :
# SCREEN        : 1 - (1 - a)(1 - b)
# SCREEN_SQRT   : 1 - sqrt((1-a)(1-b))
# SCREEN_SQUARES: 1 - [(1-a)(1-b)]**2
# COLOR_DODGE   : a / (1 - b)
# ADD           : adds point by point one image to another
# LIGHTER_COLOR : max(aR*0.2126 + aG*0.7152 + aB*0.0722,bR*0.2126 + bG*0.7152 + bB*0.0722)
# OVERLAY       : if a < 0.5: 2ab, else: 1 - 2(1-a)(1-b)
# TODO implement SOFT_LIGHT blend mode
# SOFT_LIGHT    :
# HARD_LIGHT    : if b < 0.5: 2ab, else: 1 - 2(1-a)(1-b)
# TODO implement VIVID_COLOR blend mode
# VIVID_LIGHT   :
# TODO implement LINEAR_LIGHT blend mode
# LINEAR_LIGHT  :
# TODO implement PIN_LIGHT blend mode
# PIN_LIGHT     :
# TODO implement HARD_MIX blend mode
# HARD_MIX      :
# DIFFERENCE           : |a - b|
# DIFFERENCE_SQUARES   : sqrt(|a^2 - b^2|)
# DIFFERENCE_CUBES     : (|a^3 - b^3|)^(1/3)
# DIFFERENCE_LOGS      : e^(|log(a) - log(b)|)
# TODO implement EXCLUSION blend mode
# EXCLUSION     :
# TODO implement SUBTRACT blend mode
# SUBTRACT      :
# TODO implement DIVIDE blend mode
# DIVIDE        :

OVERFLOW_HANDLING = WRAP_BACK
# CLAMP       : all values bigger than 1 are set to 1, all values smaller than 0 are set to 0
# WRAP_AROUND : the values are wrapped around 0 and 1
# WRAP_BACK   : easier to explain by example. if one value is 1.1 and the maximum allowed value is 1,
#               the new value will be 1 - (1.1 - 1)

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = 'gradient.jpg'

### END OF SCRIPT HEADER #################################################
##########################################################################

image_bottom = normalize_tensor(load_keukenhof())
# image_bottom = normalize_tensor(load_keukenhof())[:,:,0]
# image_bottom = np.repeat(image_bottom[:,:,0].flatten(),3).reshape(image_bottom.shape)
# image_bottom = np.ones_like(image_bottom)*0.5
# image_bottom = generate_horizontal_gradient(image_bottom.shape, 1, 0,gamma=1)

image_top = generate_horizontal_gradient(image_bottom.shape, 0, 1,gamma=1)

if BLEND_MODE == DARKEN:
    image_blended = np.copy(image_bottom)
    mask = np.logical_not(image_bottom < image_top)
    image_blended[mask] = image_top[mask]

if BLEND_MODE == COLOR_BURN:
    image_blended = np.copy(image_bottom)
    mask = image_top == 0
    mask_inverse = np.logical_not(mask)

    image_blended[mask] = 0
    image_blended[mask_inverse] = 1 - (1 - image_bottom[mask_inverse]) / image_top[mask_inverse]

elif BLEND_MODE == MULTIPLY:
    image_blended = image_bottom * image_top

elif BLEND_MODE == DARKER_COLOR:
    CR = 0.2126
    CG = 0.7152
    CB = 0.0722

    t1 = image_bottom[:,:,C.R] * CR + image_bottom[:,:,C.G]*CG + image_bottom[:,:,C.B]*CB
    t2 = image_top[:,:,C.R] * CR    + image_top[:,:,C.G]*CG    + image_top[:,:,C.B]*CB
    mask = t2 < t1
    mask = np.repeat(mask.flatten(),3).reshape(image_bottom.shape)

    image_blended = np.copy(image_bottom)
    image_blended[mask] = image_top[mask]


elif BLEND_MODE == LIGHTEN:
    image_blended = np.copy(image_bottom)
    mask = image_bottom < image_top
    image_blended[mask] = image_top[mask]

if BLEND_MODE == COLOR_DODGE:
    image_blended = np.copy(image_bottom)
    mask = image_top == 1
    mask_inverse = np.logical_not(mask)
    image_blended[mask] = 1
    image_blended[mask_inverse] = image_bottom[mask_inverse] / (1 - image_top[mask_inverse])

elif BLEND_MODE == OVERLAY:
    image_blended = np.copy(image_bottom)
    mask = image_bottom < 0.5
    mask_inverse = np.logical_not(mask)

    image_blended[mask] = 2*image_bottom[mask]*image_top[mask]
    image_blended[mask_inverse] = 1 - 2*(1-image_bottom[mask_inverse])*(1-image_top[mask_inverse])

elif BLEND_MODE == HARD_LIGHT:
    image_blended = np.copy(image_bottom)
    mask = image_top < 0.5
    mask_inverse = np.logical_not(mask)

    image_blended[mask] = 2*image_bottom[mask]*image_top[mask]
    image_blended[mask_inverse] = 1 - 2*(1-image_bottom[mask_inverse])*(1-image_top[mask_inverse])


elif BLEND_MODE == SCREEN:
    image_blended = 1 - (1 - image_bottom)*(1 - image_top)

elif BLEND_MODE == SCREEN_SQRT:
    image_blended = 1 - np.sqrt((1 - image_bottom) * (1 - image_top))

elif BLEND_MODE == SCREEN_SQUARES:
    image_blended = 1 - ((1 - image_bottom) * (1 - image_top))**2

elif BLEND_MODE == ADD:
    image_blended = image_bottom + image_top

elif BLEND_MODE == LIGHTER_COLOR:
    CR = 0.2126
    CG = 0.7152
    CB = 0.0722

    t1 = image_bottom[:,:,C.R] * CR + image_bottom[:,:,C.G]*CG + image_bottom[:,:,C.B]*CB
    t2 = image_top[:,:,C.R] * CR    + image_top[:,:,C.G]*CG    + image_top[:,:,C.B]*CB
    mask = t2 > t1
    mask = np.repeat(mask.flatten(),3).reshape(image_bottom.shape)

    image_blended = np.copy(image_bottom)
    image_blended[mask] = image_top[mask]

elif BLEND_MODE == DIFFERENCE:
    image_blended = np.abs(image_top - image_bottom)

elif BLEND_MODE == DIFFERENCE_SQUARES:
    image_blended = np.sqrt(np.abs(
        np.power(image_top,2) - np.power(image_bottom,2)))

elif BLEND_MODE == DIFFERENCE_CUBES:
    image_blended = np.power(np.abs(
        np.power(image_top,3) - np.power(image_bottom,3)),1./3)

elif BLEND_MODE == HANN_DIFFERENCE:
    diff = np.abs(image_top - image_bottom)
    image_blended = 0.5*(1 - np.cos(2*np.pi*diff))


if OVERFLOW_HANDLING == CLAMP:
    image_blended[image_blended>1] = 1
    image_blended[image_blended<0] = 0
elif OVERFLOW_HANDLING == WRAP_AROUND:
    mask_1 = image_blended > 1
    mask_2 = image_blended < 0
    mask = np.logical_or(mask_1,mask_2)
    image_blended[mask] = image_blended[mask] % 1.
elif OVERFLOW_HANDLING == WRAP_BACK:
    # reduction of the expresion 1 - ( x - 1 )
    mask_1 = image_blended > 1
    mask_2 = image_blended < 0
    mask = np.logical_or(mask_1,mask_2)
    image_blended[mask] = 1 - (image_blended[mask] % 1.)

if BEFORE_AFTER_COMPARISON == YES:
    t = np.append(image_top, image_bottom, axis=1)
    image_blended = np.append(t,image_blended,axis=1)

export_image(EXPORT_NAME,image_blended)
