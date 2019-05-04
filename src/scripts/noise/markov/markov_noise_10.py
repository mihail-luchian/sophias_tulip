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
N = 200
SEED = config.get('seed',0)
HEIGHT = 500
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


STRING_COLORS_1 = config.get(
    'colors_1','b3b4d4-e4f097-edd1ad-e9a6b4-ffe572')
STRING_COLORS_2 = config.get(
    'colors_2','b3b4d4-e4f097-edd1ad-e9a6b4-ffe572')

STRING_COLORS_3 = config.get(
    'colors_3','b3b4d4-e4f097-edd1ad-e9a6b4-ffe572')

COLOR_DICT_1 = {
    i:j
    for i,j in enumerate(STRING_COLORS_1.split('-'))
}

COLOR_DICT_2 = {
    i:j
    for i,j in enumerate(STRING_COLORS_2.split('-'))
}

COLOR_DICT_3 = {
    i:j
    for i,j in enumerate(STRING_COLORS_3.split('-'))
}


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def generate_patch(height, width, color_dict, direction):


    t = r.choice([0,1],p=[0.9,0.1])
    # t = r.choice([0,1],p=[1,0])

    if t == 0:
    ### markov stuff
        pattern = m.RMM([0, 1, 2, 3, 4], self_length=100, sinks=0, reduce_sinks=5)
        pattern = m.SProg(values=pattern)
        if direction == 1:
            sample = m.sample_markov_hierarchy(pattern, width)
            sample = np.repeat(sample, repeats=r.choice([1,2,3,4],size=width))
            sample = sample[:width]
            patch = np.tile(sample,reps = height)
        elif direction == -1:
            sample = m.sample_markov_hierarchy(pattern, height)
            sample = np.repeat(sample, repeats=r.choice([1,2,3,4,5],size=height))
            sample = sample[:height]
            patch = np.repeat(sample,repeats = width)
        patch = patch[:width*height]
        patch = patch.reshape(height,width)

    elif t==1:
        if direction == 1:
            patch = r.choice([0,1,2],size=width*height)
            patch = np.repeat(patch, repeats=r.choice([20,30,40,50],size=width*height))
            patch = patch[:height * width]
            patch = patch.reshape(height,width)
            patch = np.repeat(patch, repeats=r.choice([2,3,10],size=height),axis=0)
            patch = patch[:height, :width]
        elif direction == -1:
            patch = r.choice([0,1,2],size=width*height)
            patch = patch.reshape(height,width)
            patch = np.repeat(patch, repeats=r.choice([2,3,4],size=height),axis=0)
            patch = patch[:height, :width]
            patch = np.repeat(patch, repeats=r.choice([20,30,40,50],size=width),axis=1)
            patch = patch[:height, :width]

    patch = color.replace_indices_with_colors(patch,color_dict)

    patch[patch<0]=0
    patch[patch>255]=255
    return patch



def generate_image(gridx, gridy, list_color_dict):


    color_keys = [
        list(i.keys())
        for i in list_color_dict
    ]
    img = np.zeros((HEIGHT,WIDTH,3))

    startx = 0
    starty = 0
    for y in np.append(gridy, HEIGHT):
        endy = y
        for x in np.append(gridx, WIDTH):
            endx = x

            height = endy - starty
            width = endx - startx
            d = r.choice([0,1,2])
            c1,c2 = r.choice(color_keys[d],size=2,replace=False)
            img[starty:endy,startx:endx] = generate_patch(
                height,width,list_color_dict[d],r.choice([1,-1]))
            startx = endx

        startx = 0
        starty = endy

    final = data.upscale_nearest(img,ny = UPSCALE_FACTOR, nx = UPSCALE_FACTOR)

    return final.astype('uint8')


### GENERATE SECTION
print('GENERATE SECTION')

for current_iteration in range(N):
    print('CURRENT_ITERATION:',current_iteration)
    r.init_def_generator(SEED+current_iteration)

    pattern1 = m.SProg(values=config.get('grid_jump_1',10),self_length=[2,3])
    pattern2 = m.SProg(values=config.get('grid_jump_2',10),self_length=[2,3])
    pattern = m.RMM(values=[pattern1,pattern2],self_length=2)
    randomsmall = m.RMM(values=config.get('grid_jump_3',10),self_length=[2,3,4])
    randombig = m.RMM(values=config.get('grid_jump_4',10),self_length=[1,2])
    parent = m.RMM(values=[pattern,randomsmall,randombig],self_length=30)
    parent = m.SProg(values=parent)


    gridx = m.sample_markov_hierarchy_with_cumsum_limit(parent, limit=WIDTH).astype('int32')
    gridy = m.sample_markov_hierarchy_with_cumsum_limit(parent, limit=WIDTH).astype('int32')


    gridx = np.cumsum(gridx)
    gridy = np.cumsum(gridy)

    gridx = gridx[gridx < WIDTH]
    gridy = gridy[gridy < HEIGHT]



    final_img = generate_image(gridx, gridy, [COLOR_DICT_1,COLOR_DICT_2, COLOR_DICT_3])
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