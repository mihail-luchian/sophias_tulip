# SCOPE - put multiple circles in image

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


NUM_BANDS = 15
HEIGHT = 500
WIDTH  = 500
N = 10


UPSCALE_FACTOR_Y = c.INSTA_SIZE // HEIGHT
UPSCALE_FACTOR_X = c.INSTA_SIZE // WIDTH


COLOR_STRING = config.get(
    'color-string',
    'First:0/2bff4b/3-1/00ffe1/3-2/00618e/3-3/bc09b6/3,Second:0/ff7b60/-1/ffe175/-2/f6ffa5/-3/ff002e/')


### SETUP section
print('SETUP SECTION')
if DUMP_PREVIOUS_EXPORTS:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')

def gradient_circle(band_len,rkey):

    template_height = NUM_BANDS*band_len
    gradient_circle = np.zeros((template_height,template_height))

    for i,p in enumerate(range(NUM_BANDS)):
        cheight = (NUM_BANDS-i)*band_len
        c = gen.circle( (template_height,template_height),cheight//2 )
        p = r.poisson_from(rkey,i+1.1,size=(template_height,template_height))
        mask = c == 1
        gradient_circle[mask] = p[mask]

    return gradient_circle


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)



    def generate_full_image(color_string,seed):
        r.init_def_generator(seed)

        rkey = r.bind_generator()
        guard_size = 200
        image = np.zeros((HEIGHT+guard_size*2,WIDTH+guard_size*2))

        num_circles = r.choice_from(rkey,[5,10,15,20,25])
        # num_circles = r.choice_from(rkey,[30,40,50,60,70,80,90,100])
        # num_circles = r.choice_from(rkey,[400,500,600,700,800])
        for i in range(num_circles):

            loopkey = r.bind_generator_from(rkey)
            band_size = r.choice_from(loopkey,np.arange(5,10))
            circle = gradient_circle(
                band_size,
                r.bind_generator_from(loopkey)
            )

            cheight,cwidth = circle.shape

            xstart = r.choice_from(loopkey,np.arange(WIDTH+100))
            ystart = r.choice_from(loopkey,np.arange(HEIGHT+100))
            image[ystart:ystart+cheight,xstart:xstart+cwidth] += circle

        image /= np.max(image)
        image = image[
                guard_size:HEIGHT+guard_size,
                guard_size:WIDTH+guard_size]


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


