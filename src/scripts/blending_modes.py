import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.image_utils import  *
from properties import *


##########################################################################
### SCRIPT HEADER ########################################################

BLEND_MODE = MULTIPLY
# TODO implement DARKEN blend mode
# DARKEN        :
# TODO implement MULTIPLY blend mode
# MULTIPLY      :
# TODO implement COLOR_BURN blend mode
# COLOR_BURN    :
# TODO implement LINEAR_BURN blend mode
# LINEAR_BURN   :
# TODO implement DARKER_COLOR blend mode
# DARKER_COLOR  :
# TODO implement LIGHTEN blend mode
# LIGHTEN       :
# TODO implement SCREEN blend mode
# SCREEN        :
# TODO implement COLOR_DODGE blend mode
# COLOR_DODGE   :
# TODO implement ADD blend mode
# ADD           :
# TODO implement LIGHTER_COLOR blend mode
# LIGHTER_COLOR :
# TODO implement OVERLAY blend mode
# OVERLAY       :
# TODO implement SOFT_LIGHT blend mode
# SOFT_LIGHT    :
# TODO implement HARD_LIGHT blend mode
# HARD_LIGHT    :
# TODO implement VIVID_COLOR blend mode
# VIVID_LIGHT   :
# TODO implement LINEAR_LIGHT blend mode
# LINEAR_LIGHT  :
# TODO implement PIN_LIGHT blend mode
# PIN_LIGHT     :
# TODO implement HARD_MIX blend mode
# HARD_MIX      :
# TODO implement DIFFERENCE blend mode
# DIFFERENCE    :
# TODO implement EXCLUSION blend mode
# EXCLUSION     :
# TODO implement SUBTRACT blend mode
# SUBTRACT      :
# TODO implement DIVIDE blend mode
# DIVIDE        :

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = 'gradient.jpg'

### END OF SCRIPT HEADER #################################################
##########################################################################

image_loaded = normalize_tensor(load_keukenhof())

image_gradient = generate_horizontal_gradient(image_loaded.shape,0,1)

if BLEND_MODE == MULTIPLY:
    image_blended = image_loaded*image_gradient

print(image_loaded.shape)
print(image_gradient.shape)
print(image_blended.shape)
if BEFORE_AFTER_COMPARISON == YES:
    t = np.append(image_gradient,image_loaded,axis=1)
    image_blended = np.append(t,image_blended,axis=1)

export_image(EXPORT_NAME,image_blended)
