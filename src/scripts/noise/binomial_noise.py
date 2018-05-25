import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.image_utils import  *
from properties import *

##########################################################################
### SCRIPT HEADER ########################################################


### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

HEIGHT = 500
WIDTH  = 1000

IMAGE_DEPTH = CHANNELS_GRAY
# CHANNELS_GRAY
# TODO implement CHANNELS_3 image depth
# CHANNELS_3

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = 'markov.png'

### END OF SCRIPT HEADER #################################################
##########################################################################


OFFSET = 0.01

image = np.empty((HEIGHT,WIDTH))
# ps = OFFSET + np.random.uniform(0.0,1-OFFSET*2,(HEIGHT,))
ps = np.random.normal(loc = 0.5, scale = 1, size = (HEIGHT,)) % 1.0

for i in range(HEIGHT):
    line = np.random.binomial(1,ps[i],(WIDTH,))
    image[i] = line

export_image(EXPORT_NAME,image)
