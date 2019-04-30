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
N = 100
SEED = config.get('seed',0)
HEIGHT = 500
WIDTH  = HEIGHT

UPSCALE_FACTOR = c.INSTA_SIZE // HEIGHT


STRING_COLORS_1 = config.get(
    'colors_1','b3b4d4-e4f097-edd1ad-e9a6b4-ffe572')
STRING_COLORS_2 = config.get(
    'colors_2','b3b4d4-e4f097-edd1ad-e9a6b4-ffe572')

COLOR_DICT_1 = {
    i:j
    for i,j in enumerate(STRING_COLORS_1.split('-'))
}

COLOR_DICT_2 = {
    i:j
    for i,j in enumerate(STRING_COLORS_2.split('-'))
}


### SETUP section
print('SETUP SECTION')
if N>1:
    file.clear_export_dir()


### FUNCTIONS section
print('FUNCTIONS SETUP')


def generate_gradient(height,width,color1,color2):
    color1 = color.srgb2cam02ucs(color.hex2rgb(color1))
    color2 = color.srgb2cam02ucs(color.hex2rgb(color2))


    color_diff = color2 - color1

    base = np.ones((height,width,3))*color1

    option = r.choice([0,2,3],p=[0.4,0.45,0.15])
    if option == 0:
        gradient = np.linspace(0,1,width)
    elif option == 1:
        length = width//2
        gradient = np.linspace(0,1,length)
        if width % 2 == 0:
            gradient = np.concatenate((gradient, gradient[::-1]))
        else:
            gradient = np.concatenate((gradient,np.array([1]),gradient[::-1]))
    elif option == 2:
        ### markov stuff
        pattern = m.RMM([0, 1, -1, 2], self_length=10, lenghts=[10, 3, 1, 4])
        pattern = m.SProg(values=pattern)
        sample = m.sample_markov_hierarchy(pattern, width)
        sample = np.cumsum(sample)
        # print(sample)
        if sample[-1] <= 0:
            sample[-1] = 1
        gradient = sample/np.max(np.abs(sample))
    else:
        gradient = np.zeros(width)

    base = base + (gradient[:,np.newaxis]*color_diff)[np.newaxis,:,:]

    patch = color.cam02ucs2srgb(base)
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
            d = r.choice([0,1])
            c1,c2 = r.choice(color_keys[d],size=2,replace=False)
            img[starty:endy,startx:endx] = generate_gradient(
                height,width,list_color_dict[d][c1],list_color_dict[d][c2])
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


    pattern1 = m.SProg(values=30,self_length=[7,8])
    pattern2 = m.SProg(values=[60,65],self_length=[3,4,5])
    pattern = m.RMM(values=[pattern1,pattern2],self_length=3)
    randomverysmall = m.RMM(values=[2,3],self_length=[2])
    randomsmall = m.RMM(values=[7,9,11],self_length=[2,3,4])
    randombig = m.RMM(values=[150,200],self_length=[1,1,2])
    parent = m.RMM(values=[pattern1,randomsmall,randombig])


    gridx = m.sample_markov_hierarchy_with_cumsum_limit(parent, limit=WIDTH).astype('int32')
    gridy = m.sample_markov_hierarchy_with_cumsum_limit(parent, limit=WIDTH).astype('int32')


    gridx = np.cumsum(gridx)
    gridy = np.cumsum(gridy)

    gridx = gridx[gridx < WIDTH]
    gridy = gridy[gridy < HEIGHT]



    final_img = generate_image(gridx, gridy, [COLOR_DICT_1,COLOR_DICT_2])
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