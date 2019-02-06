import numpy as np
from utils.generate_utils import *
from utils.file_utils import *
from utils.data_utils import  *
from properties import *

##########################################################################
### SCRIPT HEADER ########################################################

HEIGHT = 500
WIDTH  = 1000

IMAGE_DEPTH = CHANNELS_GRAY
# CHANNELS_GRAY
# TODO implement CHANNELS_3 image depth
# CHANNELS_3

### NON SCRIPT SPECIFIC OPTIONS ##########################################

# concat the input with the output for comparison purposes
BEFORE_AFTER_COMPARISON = YES

# Name of the export file. By specifying an extension you also specify the format of the export
EXPORT_NAME = '0.png'

### END OF SCRIPT HEADER #################################################
##########################################################################


OFFSET = 0.01


markov_process_change_line_type = OFFSET + np.random.uniform(0.0, 1 - OFFSET * 2, (2,))
markov_process_change_line_properties = OFFSET + np.random.uniform(0.0, 1 - OFFSET * 2, (2,))
markov_process_change_line_properties = [0.05, 0.1]
image = np.ones((HEIGHT,WIDTH))

current_state_pixel = 0
current_state_line = 0
current_state_line_properties = 0
for h in np.arange(HEIGHT):
    current_state_line = np.random.binomial(
        1, markov_process_change_line_type[current_state_line], (1,))[0]
    if current_state_line == 1:
        current_state_line_properties = np.random.binomial(
                1, markov_process_change_line_properties[current_state_line_properties], (1,))[0]
        if current_state_line_properties == 1:
            ps = OFFSET + np.random.uniform(0.0, 1 - OFFSET * 2, (2,))
        for w in np.arange(WIDTH):
            current_state_pixel = np.random.binomial(1, ps[current_state_pixel], (1,))[0]
            image[h,w] = current_state_pixel

export_image(EXPORT_NAME,image)
