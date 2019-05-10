print('IMPORTING MODULES')
import time
import constants as c
import script_config as config
import numpy as np
import cv2
import utils.generate_utils as gen
import random_manager as r
import utils.file_utils as file
import utils.data_utils as data
import utils.markov_utils as m
import utils.color_utils as color
import utils.viz_utils as viz

### DATA/INPUT/SHARED by all runs section
print('PREPARING DATA SECTION')
N = 2
SEED = config.get('seed',0)
HEIGHT = 1000
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


STRING_COLORS_1 = config.get('string_colors_1',c.DEFAULT_COLOR_STR)
STRING_COLORS_2 = config.get('string_colors_2',c.DEFAULT_COLOR_STR)
STRING_COLORS_3 = config.get('string_colors_3',c.DEFAULT_COLOR_STR)
STRING_COLORS_4 = config.get('string_colors_4',c.DEFAULT_COLOR_STR)
COLOR_DICT_1 = color.build_color_dictionary(STRING_COLORS_1)
COLOR_DICT_2 = color.build_color_dictionary(STRING_COLORS_2)
COLOR_DICT_3 = color.build_color_dictionary(STRING_COLORS_3)
COLOR_DICT_4 = color.build_color_dictionary(STRING_COLORS_4)


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def continous_linspace(values,lengths):
    transitions = np.concatenate(
        [
            np.linspace(0,1,lengths[i])
            for i in range(len(values)-1)
    ])


    bins = np.arange(6)/6
    digitized = np.digitize(transitions,bins)
    transitions = bins[digitized-1]

    transitions = data.ease_inout_sine(transitions)
    values_start = values[:-1]
    values_end = values[1:]

    return (
            np.repeat(values_start,lengths.astype('int32'))*(1-transitions)
            + transitions*np.repeat(values_end,lengths.astype('int32'))
    )

def generate_gradient(colors,lengths):
    # print(colors.shape)
    # print(lengths.shape)

    colors = color.srgb2cam02ucs(colors)

    j = colors[:,0]
    c = colors[:,1]
    h = colors[:,2]

    return color.cam02ucs2srgb(
        np.stack(
            (
                continous_linspace(j,lengths),
                continous_linspace(c,lengths),
                continous_linspace(h,lengths),
            ),
            axis=1,
        )
    )

def generate_patch(height, width, list_color_dicts):


    d = r.choice(len(list_color_dicts))
    patch = np.zeros((height,width,3),dtype='float64')

    pattern = m.RMM(values=[0,1,2,3,4],self_length=100)
    num_samples = width//5
    sample = m.sample_markov_hierarchy(pattern,num_samples)
    sample = color.replace_indices_with_colors(sample,list_color_dicts[d])

    start = np.ones(num_samples)*60
    start = np.cumsum(start)
    offsets = r.choice([-1,0,1],p=[0.05,0.9,0.05],size=(height,num_samples))
    offsets = np.cumsum(offsets,axis=0) + start

    i = 0
    while i < height:
        diff = np.diff(offsets[i])
        multiples = r.choice([3,4,5])
        gradient = generate_gradient(sample,diff)[:width]
        patch[i:i+multiples] = gradient[None,:]
        i += multiples

    patch[patch<0]=0
    patch[patch>255]=255
    return patch



def generate_image(gridx, gridy, list_color_dict):

    color_keys = [
        list(i.keys())
        for i in list_color_dict
    ]
    img = np.zeros((HEIGHT,WIDTH,3),dtype='float64')

    startx = 0
    starty = 0

    for y in np.append(gridy, HEIGHT):
        endy = y
        for x in np.append(gridx, WIDTH):
            endx = x

            height = endy - starty
            width = endx - startx
            patch = generate_patch(height,width,list_color_dict)
            img[starty:endy,startx:endx] = patch
            startx = endx

        startx = 0

        img[starty:endy] = np.roll(img[starty:endy],shift=r.choice(6)*50,axis=1)


        starty = endy


    final = data.upscale_nearest(img,ny = UPSCALE_FACTOR, nx = UPSCALE_FACTOR)

    return final.astype('uint8')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    r.init_def_generator(SEED+current_iteration)

    gridpattern = m.RMM(values=np.arange(300,400,5),self_length=10)
    parent = m.SProg(values=gridpattern)

    gridx = m.generate_grid_lines(parent,WIDTH)
    gridy = m.generate_grid_lines(parent,HEIGHT)

    print(gridx)
    print(gridy)

    final_img = generate_image(
        gridx, gridy,
        [COLOR_DICT_1,COLOR_DICT_2,COLOR_DICT_3,COLOR_DICT_4])

    file.export_image(
        '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
        final_img.astype('uint8'),format='png')
