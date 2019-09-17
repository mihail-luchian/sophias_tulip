# SCOPE - let's find the threshold for more p values
# RESULT - for values around 0 - the difference becomes noticeable more than 0.01, then it increases to 0.1 for p around 0.5 and back again to 0.01

print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import utils.generate_utils as gen
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
DUMP_PREVIOUS_EXPORTS = True
START_SERVER = False
SAVE_IMAGES = True
SEED = config.get('seed',296)
HEIGHT = 500
WIDTH  = 500
SEGMENT_LENGTH = 40

PS = [
    (0.01,0.02),
    (0.015,0.03),
    (0.02,0.035),
    (0.06,0.08),
    (0.075,0.1),
    (0.1,0.14),
    (0.2,0.25),
    (0.3,0.35),
    (0.4,0.5),
    (0.5,0.6),
    (0.6,0.7),
    (0.8,0.86),
    (0.9,0.95),
    (0.98,0.99),
]
N = len(PS)


UPSCALE_FACTOR_Y = c.INSTA_SIZE // HEIGHT
UPSCALE_FACTOR_X = c.INSTA_SIZE // WIDTH


COLOR_STRING = config.get(
    'color-string',
    'First:0/2bff4b/3-1/00ffe1/3-2/00618e/3-3/bc09b6/3,Second:0/ff7b60/-1/ffe175/-2/f6ffa5/-3/ff002e/')


### SETUP section
print('SETUP SECTION')
if DUMP_PREVIOUS_EXPORTS:
    file.clear_export_folder()


### FUNCTIONS section
print('FUNCTIONS SETUP')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)



    def generate_full_image(color_string,seed):
        r.init_def_generator(seed)

        rkey = r.bind_generator()
        image = np.zeros((HEIGHT,WIDTH))

        p1,p2 = PS[current_iteration]
        print(p1,p2)


        image[:,:WIDTH//2] = r.binomial_from(rkey,1,p1,size=(HEIGHT,WIDTH//2))
        image[:,WIDTH//2:] = r.binomial_from(rkey,1,p2,size=(HEIGHT,WIDTH//2))



        return  data.upscale_nearest(
            data.prepare_image_for_export(image*255),
            ny=UPSCALE_FACTOR_Y,
            nx=UPSCALE_FACTOR_X
        )

    if START_SERVER is True:
        viz.start_image_server(
            generate_full_image,
            COLOR_STRING,
            SEED+current_iteration)
        break
    elif SAVE_IMAGES is True:
        image = generate_full_image(COLOR_STRING,SEED+current_iteration)
        file.export_image(
            '%d_%d_%d' % (current_iteration,SEED+current_iteration,int(round(time.time() * 1000))),
            image,format='png')
    else:
        generate_full_image(COLOR_STRING, SEED + current_iteration)


