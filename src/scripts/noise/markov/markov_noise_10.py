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
N = 10
SEED = config.get('seed',0)
HEIGHT = 500
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


STRING_COLORS = config.get(
    'colors','b3b4d4-e4f097-edd1ad-e9a6b4-ffe572')

COLOR_DICT = {
    i:j
    for i,j in enumerate(STRING_COLORS.split('-'))
}

COLOR_DICT = {
    **COLOR_DICT,
}


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def to_string_pattern(p,values):
    dictionary_pos = {
        values[i]:i
        for i in range(len(values))
    }

    poss = [
        dictionary_pos[i]
        for i in p
    ]

    return ''.join(c.PATTERN_INDICES_STR[i] for i in poss)



def generate_color_image(gridx,gridy,color_dict):


    color_keys = list(color_dict.keys())
    img = np.zeros((HEIGHT,WIDTH))

    startx = 0
    starty = 0
    for y in np.append(gridy, HEIGHT):
        endy = y
        for x in np.append(gridx, WIDTH):
            endx = x

            img[starty:endy,startx:endx] = r.choice(color_keys)
            startx = endx

        startx = 0
        starty = endy

    final = color.replace_indices_with_colors(img,color_dict)
    final = data.upscale_nearest(final,ny = UPSCALE_FACTOR, nx = UPSCALE_FACTOR)

    return final.astype('uint8')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    r.init_def_generator(SEED+current_iteration)


    pattern1 = m.SProg(values=10,self_length=[4,5])
    pattern2 = m.SProg(values=[20,25],self_length=[3,4,5])
    pattern = m.RMM(values=[pattern1,pattern2],self_length=3)
    randomsmall = m.RMM(values=[3,4,5,6,7],self_length=[2,3,4])
    randombig = m.RMM(values=[400,500],self_length=[1])
    parent = m.RMM(values=[pattern1,randomsmall,randombig])


    gridx = m.sample_markov_hierarchy_with_cumsum_limit(parent, limit=WIDTH).astype('int32')
    gridy = m.sample_markov_hierarchy_with_cumsum_limit(parent, limit=WIDTH).astype('int32')


    gridx = np.cumsum(gridx)
    gridy = np.cumsum(gridy)

    gridx = gridx[gridx < WIDTH]
    gridy = gridy[gridy < HEIGHT]



    final_img = generate_color_image(gridx,gridy,COLOR_DICT)
    file.export_image(
        '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
        final_img.astype('uint8'),format='png')


    # if N==1:
    #     viz.start_color_editing_tool(
    #         blueprint=img_acum,
    #         color_dict=COLOR_DICT,
    #         downsample=2,
    #         gen_fun = lambda x, color_dict: generate_color_image(x, colors_acum[:, ::2], color_dict) )
    # else:
    #     final_img = generate_color_image(img_acum, colors_acum, COLOR_DICT)
    #     file.export_image(
    #         '%d_%d' % (current_iteration,int(round(time.time() * 1000))),
    #         final_img.astype('uint8'),format='png')