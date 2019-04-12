print('IMPORTING MODULES')
import time
import constants as c
import numpy as np
import cv2
import utils.generate_utils as gen
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
N = 5
SEED = 4210468
HEIGHT = 50
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT

START_COLOR = color.hex2hsv('465775')
print(START_COLOR)


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def gen_portion(parent,height,width,tile_height=None,tile_width=None):
    img = m.paint_linearly_markov_hierarchy(
        markov_tree=parent,
        width=width, height=height,tile_width=tile_width,tile_height=tile_height)
    return img.reshape(img.shape[0],img.shape[1])


def gen_walk_pattern(num_candidates,pattern_length):
    p = np.random.choice(num_candidates,pattern_length,replace=False)
    s = ''.join([ str(i) for i in p ])
    s = s+s[::-1]
    return s

def to_string_pattern(p,values):
    dictionary_pos = {
        values[i]:i
        for i in range(len(values))
    }

    poss = [
        dictionary_pos[i]
        for i in p
    ]

    return ''.join(str(i) for i in poss)


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    np.random.seed(SEED+current_iteration)

    skips = [-5,5, -10,10, -15,15, -20,20, 0]



    patterns = [
        [
            -5,5,
            -10,10,
            -15,15,
            -10,10,
            -5,5
        ],
        [
            -5,0,0,
            10,0,0,
            -5,0,0,0,
        ],
        [
            5,
            10,
            15,
            20,
            0,0
            -20,
            -15,
            -10,
            -5,
        ],
    ]

    patterns = [
        to_string_pattern(i,skips)
        for i in patterns
    ]

    print(patterns)

    patterns = [
        m.SimplePattern(pattern=p,candidates=skips)
        for p in patterns
    ]

    child_lengths = [2*WIDTH//5-1,3*WIDTH//5-1]
    model = m.Processor(
        m.RandomMarkovModel(values=patterns,child_lengths=child_lengths),
        num_tiles=[1,2,3], length_limit=WIDTH)

    parent = m.SimpleProgression(values=model,child_lengths=5)

    img = gen_portion(parent,HEIGHT,WIDTH)
    default_color = np.ones((HEIGHT,WIDTH,3)) *  START_COLOR

    img_acum = np.cumsum(img,axis=1)
    layer_hue = img_acum + default_color[:, :, 0]
    layer_saturation = default_color[:, :, 1] - img_acum
    layer_value = img_acum + default_color[:, :, 2]

    ls = np.stack((layer_hue, layer_saturation, layer_value), axis=2)
    final_img = data.upscale_nearest(ls,UPSCALE_FACTOR)
    final_img = color.clamp_hsv_opencv(final_img)
    final_img = cv2.cvtColor(final_img,cv2.COLOR_HSV2RGB)*255
    file.export_image(
        '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
        final_img.astype('uint8'),format='png')
